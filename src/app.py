from web3 import Web3, HTTPProvider
from flask import Flask, render_template, redirect, request, jsonify, session
import json
import bcrypt
from werkzeug.utils import secure_filename
import os
import hashlib

userManagementArtifactPath = "../build/contracts/userManagement.json"
blockchainServer = "HTTP://127.0.0.1:7545"

def connectWithContract(wallet, artifact=userManagementArtifactPath):
    web3 = Web3(HTTPProvider(blockchainServer))  # it is connecting with server
    print('Connected with Blockchain Server')

    if wallet == 0:
        web3.eth.defaultAccount = web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount = wallet
    print('Wallet Selected')

    with open(artifact) as f:
        artifact_json = json.load(f)
        contract_abi = artifact_json['abi']
        contract_address = artifact_json['networks']['5777']['address']

    contract = web3.eth.contract(abi=contract_abi, address=contract_address)
    print('Contract Selected')
    return contract, web3

app = Flask(__name__)
app.secret_key = "1234567890"

@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/consumerlogin')
def loginPage():
    return render_template('consumerlogin.html')

@app.route('/retaailerlogin')
def retailerlogin():
    return render_template('retailerlogin.html')

@app.route('/manufacturerlogin')
def manufacturerlogin():
    return render_template('manufacturerlogin.html')

@app.route('/consumersignup')
def signupPage():
    return render_template('consumersignup.html')

@app.route('/retailersignup')
def retailsignuppage():
    return render_template('retailersignup.html')

@app.route("/manufacturersignup")
def manufacsignup():
    return render_template('manufacturersignup.html')
@app.route("/form")
def form():
    return render_template("manufacturerform.html")
@app.route('/register', methods=['POST'])
def register():
    role = request.form['role']
    wallet = request.form['account']
    username = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirmPassword = request.form['confirmPassword']

    if password != confirmPassword:
        if role == "consumer":
            return render_template("consumersignup.html", message='Passwords do not match. Try again.')
        elif role == "Manufacturer":
            return render_template("manufacturersignup.html", message='Passwords do not match. Try again.')
        elif role == "retailer":
            return render_template("retailersignup.html", message='Passwords do not match. Try again.')
        else:
            return render_template("index.html")

    contract, web3 = connectWithContract(wallet)  # UserManagement
    try:
        tx_hash = contract.functions.userSignUp(wallet, username, password, role, email).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        print('Transaction Successful')
        if role == "consumer":
            return render_template("consumersignup.html", message='Signup Successful')
        elif role == "Manufacturer":
            return render_template("manufacturersignup.html", message='Signup Successful')
        elif role == "retailer":
            return render_template("retailersignup.html", message='Signup Successful')
    except:
        return render_template('signup.html', message='There was a problem creating the account.')
    
@app.route('/manufacturerDashboard')
def manufacturerDashboard():
    return render_template("manufacturerHome.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']  # Get username from the login form
    password = request.form['password']  # Get password from the login form
    
    # Connect to the smart contract
    contract, web3 = connectWithContract(0)  # Use default wallet for contract connection

    try:
        # Check if the login credentials are valid
        is_valid = contract.functions.userLogin(username, password).call()
        if is_valid:
            # Fetch the user details by username (this will return a tuple)
            user_details = contract.functions.viewUserByUsername(username).call()

            # The user_details is a tuple, so we need to extract the values accordingly
            user_wallet = user_details[0]  # User's wallet address
            user_name = user_details[1]    # User's username
            user_role = user_details[3]    # User's role
            user_email = user_details[4]   # User's email

            # Store user details in session
            session['userwallet'] = user_wallet
            session['username'] = user_name
            session['userrole'] = user_role
            session['useremail'] = user_email

            # Redirect based on the user's role
            if session['userrole'] == 'consumer':
                return redirect('/consumerDashboard')  # Consumer-specific dashboard
            elif session['userrole'] == 'retailer':
                return redirect('/retailerDashboard')  # Retailer-specific dashboard
            elif session['userrole'] == 'Manufacturer':
                return redirect('/manufacturerDashboard')  # Manufacturer-specific dashboard
            else:
                return render_template('index.html', message='Role not recognized. Contact support.')

        else:
            return render_template('index.html', message='Invalid username or password. Try again.')

    except Exception as e:
        print(f"Error during login: {e}")
        return render_template('index.html', message='Error logging in. Please try again later.')

@app.route('/addProduct', methods=['POST'])
def add_product():
    # Check if the manufacturer is logged in
    if 'userwallet' not in session or session['userrole'] != 'Manufacturer':
        return jsonify({'message': 'Unauthorized access. Please log in as a Manufacturer.'}), 401

    # Get the details from the form
    product_id = request.form['product_id']
    product_name = request.form['product_name']
    manufacture_date = request.form['manufacture_date']
    product_image = request.files['product_image']

    # Ensure 'static/uploads' directory exists
    upload_dir = os.path.join('static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Securely save the image temporarily
    filename = secure_filename(product_image.filename)
    image_path = os.path.join(upload_dir, filename)
    product_image.save(image_path)

    # Generate a hash of the product image for uniqueness verification
    with open(image_path, 'rb') as img_file:
        image_hash = hashlib.sha256(img_file.read()).hexdigest()

    # Connect to the ProductManagement contract
    contract, web3 = connectWithContract(
        session['userwallet'], artifact="../build/contracts/ProductManagement.json"
    )

    try:
        # Add product to the blockchain
        tx_hash = contract.functions.addProduct(
            session['userwallet'], product_id, product_name, manufacture_date, image_hash
        ).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)

        # Success response
        return jsonify({'message': 'Product added successfully.'}), 200

    except Exception as e:
        print(f"Error adding product: {e}")
        return jsonify({'message': 'Error adding product. Please try again later.'}), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7000, debug=True)

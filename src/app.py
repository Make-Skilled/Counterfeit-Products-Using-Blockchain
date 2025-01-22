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
        return render_template('index.html', message='There was a problem creating the account.')
    
@app.route('/manufacturerDashboard')
def manufacturerDashboard():
    if 'userwallet' not in session or session['userrole'] != 'Manufacturer':
       return redirect('/manufacturerlogin')
    return render_template("manufacturerHome.html")

@app.route('/consumerDashboard')
def consumer_dashboard():
    # Ensure the user is logged in as a Consumer
    if 'userwallet' not in session or session['userrole'] != 'consumer':
        return redirect('/consumerlogin')  # Redirect to the login page if not authenticated
    return render_template('consumerHome.html')  # Replace with your consumer dashboard HTML page


@app.route('/retailerDashboard')
def retailer_dashboard():
    # Ensure the user is logged in as a Retailer
    if 'userwallet' not in session or session['userrole'] != 'retailer':
        return redirect('/retaailerlogin')  # Redirect to the login page if not authenticated
    return render_template('retailerHome.html')  # Replace with your retailer dashboard HTML page


@app.route('/getProductDetails', methods=['GET'])
def get_product_details():
    # Ensure the user is logged in as a Retailer
    if 'userwallet' not in session or session['userrole'] != 'consumer':
        return jsonify({'message': 'Unauthorized access. Please log in as a Retailer.'}), 401

    # Get the product hash from the query parameters
    product_hash = request.args.get('hash')

    if not product_hash:
        return jsonify({'message': 'No product hash provided.'}), 400

    try:
        # Connect to the ProductManagement contract
        contract, web3 = connectWithContract(
            session['userwallet'], artifact="../build/contracts/ProductManagement.json"
        )

        # Get the product ID by product hash
        product_id = contract.functions.getProductIdByHash(product_hash).call()

        if not product_id:
            return jsonify({'message': 'Product not found.'}), 404

        # Fetch product details by product ID
        details = contract.functions.getProductDetails(product_id).call()

        # Prepare the product details
        product_details = {
            'manufacturer': details[0],  # Manufacturer address
            'productId': details[1],
            'productName': details[2],
            'manufactureDate': details[3],
            'filePath': details[5]
        }

        # Fetch manufacturer details using the manufacturer address
        manufacturer_address = details[0]  # Manufacturer's wallet address

        # Connect to the UserManagement contract
        user_contract, user_web3 = connectWithContract(
            manufacturer_address, artifact="../build/contracts/userManagement.json"
        )

        # Fetch manufacturer details
        manufacturer_details = user_contract.functions.viewUserByWallet(manufacturer_address).call()

        manufacturer_data = {
            'manufacturerName': manufacturer_details[1],  # Manufacturer's name
            'manufacturerEmail': manufacturer_details[4],  # Manufacturer's email
            'manufacturerRole': manufacturer_details[3]  # Manufacturer's role
        }

        # Return product details along with manufacturer details
        return jsonify({'product': product_details, 'manufacturer': manufacturer_data}), 200

    except Exception as e:
        print(f"Error fetching product details: {e}")
        return jsonify({'message': 'Error fetching product details. Please try again later.'}), 500



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
                print("manufacturer")
                return redirect('/manufacturerDashboard')  # Manufacturer-specific dashboard
            else:
                return render_template('index.html', message='Role not recognized. Contact support.')

        else:
            return render_template('index.html', message='Invalid username or password. Try again.')

    except Exception as e:
        print(f"Error during login: {e}")
        return render_template('index.html', message='Error logging in. Please try again later.')
    

@app.route('/getRetailers', methods=['GET'])
def get_retailers():
    try:
        # Connect to the UserManagement contract
        contract, web3 = connectWithContract(0)  # Use default wallet for contract connection

        # Fetch all users
        users = contract.functions.viewAllUsers().call()

        # Filter users with the role "retailer"
        retailers = [
            {'wallet': user[0], 'name': user[1], 'email': user[4]}
            for user in users if user[3] == "retailer"
        ]

        return jsonify({'retailers': retailers}), 200

    except Exception as e:
        print(f"Error fetching retailers: {e}")
        return jsonify({'message': 'Error fetching retailers. Please try again later.'}), 500


@app.route('/addingProduct', methods=['POST'])
def add_product():
    # Check if the manufacturer is logged in
    if 'userwallet' not in session or session['userrole'] != 'Manufacturer':
        return jsonify({'message': 'Unauthorized access. Please log in as a Manufacturer.'}), 401

    # Get the details from the form
    product_id = request.form['product_id']
    product_name = request.form['product_name']
    manufacture_date = request.form['manufacture_date']
    retailer_address = request.form['retailer']  # Get selected retailer address
    product_file = request.files['product_image']

    # Ensure 'static/uploads' directory exists
    upload_dir = os.path.join('static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Securely save the uploaded file
    filename = secure_filename(product_file.filename)
    file_path = os.path.join(upload_dir, filename)
    product_file.save(file_path)

    # Connect to the ProductManagement contract
    try:
        contract, web3 = connectWithContract(
            session['userwallet'], artifact="../build/contracts/ProductManagement.json"
        )
    except Exception as e:
        print(f"Error connecting to contract: {e}")
        return jsonify({'message': 'Error connecting to contract.'}), 500

    # Validate retailer address
    if not web3.isAddress(retailer_address):
        return jsonify({'message': 'Invalid retailer address.'}), 400

    # Generate a unique hash for the product
    product_hash = hashlib.sha256((product_id + product_name + manufacture_date).encode()).hexdigest()

    try:
        # Add product to the blockchain
        tx_hash = contract.functions.addProduct(
            product_id, product_name, manufacture_date, product_hash, file_path, retailer_address
        ).transact({'from': session['userwallet']})
        web3.eth.waitForTransactionReceipt(tx_hash)

        # Success response
        return jsonify({'message': 'Product added successfully.'}), 200

    except Exception as e:
        print(f"Error adding product: {e}")
        return jsonify({'message': 'Error adding product. Please try again later.'}), 500


@app.route('/manufacturerProducts')
def manufacturer_products_page():
    # Ensure the user is logged in as a Manufacturer
    if 'userwallet' not in session or session['userrole'] != 'Manufacturer':
        return redirect('/manufacturerlogin')  # Redirect to the login page if not authenticated
    return render_template('productdetails.html')

@app.route('/getManufacturerProducts', methods=['GET'])
def get_manufacturer_products():
    if 'userwallet' not in session or session['userrole'] != 'Manufacturer':
        return jsonify({'message': 'Unauthorized access. Please log in as a Manufacturer.'}), 401

    try:
        # Connect to the ProductManagement contract
        contract, web3 = connectWithContract(
            session['userwallet'], artifact="../build/contracts/ProductManagement.json"
        )

        # Fetch the product IDs associated with the logged-in manufacturer
        product_ids = contract.functions.getProductsByManufacturer(session['userwallet']).call()

        # Initialize a list to store product details
        products = []

        # Fetch details for each product ID
        for product_id in product_ids:
            details = contract.functions.getProductDetails(product_id).call()

            # Log the product details to see the returned data structure
            print(f"Product details for product ID {product_id}: {details}")

            # Extract retailer address from product details
            retailer_address = details[1]  # Retailer address is at index 1 in the returned details

            # Fetch retailer details using the retailer address
            user_contract, user_web3 = connectWithContract(
                retailer_address, artifact="../build/contracts/userManagement.json"
            )
            retailer_details = user_contract.functions.viewUserByWallet(retailer_address).call()

            # Log retailer details to verify the data
            print(f"Retailer details for address {retailer_address}: {retailer_details}")

            # Prepare product details along with retailer's name and email
            products.append({
                'manufacturer': details[0],     # Manufacturer address
                'retailer': {
                    'name': retailer_details[1],         # Retailer name
                    'email': retailer_details[4]        # Retailer email
                },
                'productId': details[2],        # Product ID
                'productName': details[3],      # Product name
                'manufactureDate': details[4],  # Manufacture date
                'productHash': details[5],      # Product hash
                'filePath': details[6]          # File path (image URL or document)
            })

        print(f"Fetched products: {products}")
        return jsonify({'products': products}), 200

    except Exception as e:
        print(f"Error fetching products: {e}")
        return jsonify({'message': 'Error fetching products. Please try again later.'}), 500


@app.route('/getRetailerProducts', methods=['GET'])
def get_retailer_products():
    if 'userwallet' not in session or session['userrole'] != 'retailer':
        return jsonify({'message': 'Unauthorized access. Please log in as a Retailer.'}), 401

    try:
        # Connect to the ProductManagement contract
        contract, web3 = connectWithContract(
            session['userwallet'], artifact="../build/contracts/ProductManagement.json"
        )

        # Get all products from all manufacturers
        manufacturer_addresses = set()  # Use a set to store unique manufacturer addresses
        products = []

        # Get all users to find manufacturers
        user_contract, _ = connectWithContract(0)
        all_users = user_contract.functions.viewAllUsers().call()
        
        # Filter manufacturers
        for user in all_users:
            if user[3] == "Manufacturer":  # Check if user role is Manufacturer
                manufacturer_addresses.add(user[0])  # Add manufacturer address to set

        # For each manufacturer, get their products and filter for the current retailer
        for manufacturer in manufacturer_addresses:
            product_ids = contract.functions.getProductsByManufacturer(manufacturer).call()
            
            for product_id in product_ids:
                details = contract.functions.getProductDetails(product_id).call()
                # Check if the current retailer is assigned to this product
                if details[1].lower() == session['userwallet'].lower():  # Compare retailer addresses
                    # Get manufacturer details
                    manufacturer_details = user_contract.functions.viewUserByWallet(details[0]).call()
                    
                    products.append({
                        'manufacturer': {
                            'address': details[0],
                            'name': manufacturer_details[1],
                            'email': manufacturer_details[4]
                        },
                        'productId': details[2],
                        'productName': details[3],
                        'manufactureDate': details[4],
                        'productHash': details[5],
                        'filePath': details[6]
                    })

        return jsonify({'products': products}), 200

    except Exception as e:
        print(f"Error fetching retailer products: {e}")
        return jsonify({'message': 'Error fetching products. Please try again later.'}), 500


@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect('/')  # Redirect to the homepage



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7000, debug=True)

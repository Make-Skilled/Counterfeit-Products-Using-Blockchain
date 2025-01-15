// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ProductManagement {
    struct Product {
        address manufacturer;    // Address of the product manufacturer
        address retailer;        // Address of the retailer
        string productId;        // Unique identifier for the product
        string productName;      // Name of the product
        string manufactureDate;  // Date of manufacture
        string productHash;      // Hash value uniquely identifying the product
        string filePath;         // Optional file path related to the product (e.g., additional data or docs)
    }

    mapping(string => Product) public products; // Mapping product ID to Product details
    mapping(address => string[]) public manufacturerProducts; // Manufacturer to list of product IDs
    mapping(string => string) public productHashToId; // Map productHash to productId

    event ProductAdded(address indexed manufacturer, address indexed retailer, string productId, string productHash);

    /// @notice Add a new product to the contract.
    /// @param productId A unique identifier for the product.
    /// @param productName The name of the product.
    /// @param manufactureDate The manufacture date of the product.
    /// @param productHash A unique hash representing the product.
    /// @param filePath An optional file path related to the product.
    /// @param retailer The address of the retailer.
    function addProduct(
        string memory productId,
        string memory productName,
        string memory manufactureDate,
        string memory productHash,
        string memory filePath,
        address retailer
    ) public {
        require(bytes(products[productId].productId).length == 0, "Product ID already exists.");
        require(bytes(productHashToId[productHash]).length == 0, "Product hash already exists.");
        require(retailer != address(0), "Retailer address cannot be zero.");

        // Create the product
        products[productId] = Product({
            manufacturer: msg.sender,
            retailer: retailer,
            productId: productId,
            productName: productName,
            manufactureDate: manufactureDate,
            productHash: productHash,
            filePath: filePath
        });

        // Map product hash to product ID
        productHashToId[productHash] = productId;

        // Link product ID to the manufacturer
        manufacturerProducts[msg.sender].push(productId);

        emit ProductAdded(msg.sender, retailer, productId, productHash);
    }

    /// @notice Get a list of products added by a manufacturer.
    /// @param manufacturer The address of the manufacturer.
    /// @return An array of product IDs.
    function getProductsByManufacturer(address manufacturer) public view returns (string[] memory) {
        return manufacturerProducts[manufacturer];
    }

    /// @notice Get the details of a product by its ID.
    /// @param productId The unique identifier of the product.
    /// @return The details of the product (manufacturer, retailer, productId, productName, manufactureDate, productHash, filePath).
    function getProductDetails(string memory productId) public view returns (
        address,
        address,
        string memory,
        string memory,
        string memory,
        string memory,
        string memory
    ) {
        Product memory product = products[productId];
        require(bytes(product.productId).length != 0, "Product does not exist.");
        return (
            product.manufacturer,
            product.retailer,
            product.productId,
            product.productName,
            product.manufactureDate,
            product.productHash,
            product.filePath
        );
    }

    /// @notice Get the product ID by its hash.
    /// @param productHash The unique hash representing the product.
    /// @return The product ID associated with the hash.
    function getProductIdByHash(string memory productHash) public view returns (string memory) {
        return productHashToId[productHash];
    }
}

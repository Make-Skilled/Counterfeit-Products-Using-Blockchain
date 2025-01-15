// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ProductManagement {
    struct Product {
        address manufacturer;
        string productId;
        string productName;
        string manufactureDate;
        string imageHash;
    }

    mapping(string => Product) public products; // Mapping product ID to Product details
    mapping(address => string[]) public manufacturerProducts; // Manufacturer to list of product IDs

    event ProductAdded(address indexed manufacturer, string productId);

    function addProduct(
        address manufacturer,
        string memory productId,
        string memory productName,
        string memory manufactureDate,
        string memory imageHash
    ) public {
        require(bytes(products[productId].productId).length == 0, "Product ID already exists.");

        // Create the product
        products[productId] = Product({
            manufacturer: manufacturer,
            productId: productId,
            productName: productName,
            manufactureDate: manufactureDate,
            imageHash: imageHash
        });

        // Link product ID to the manufacturer
        manufacturerProducts[manufacturer].push(productId);

        emit ProductAdded(manufacturer, productId);
    }

    function getProductsByManufacturer(address manufacturer) public view returns (string[] memory) {
        return manufacturerProducts[manufacturer];
    }

    function getProductDetails(string memory productId) public view returns (
        address, string memory, string memory, string memory, string memory
    ) {
        Product memory product = products[productId];
        require(bytes(product.productId).length != 0, "Product does not exist.");
        return (
            product.manufacturer,
            product.productId,
            product.productName,
            product.manufactureDate,
            product.imageHash
        );
    }
}

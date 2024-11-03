# Kapital Payment Gateway Client

`kapital` is a Python client for the Kapital Bank payment gateway, designed to simplify the process of creating and managing payment orders. This library provides a straightforward interface to interact with the Kapital Bank API, making it easier to integrate payment functionality into your applications.

## Features

- Create payment orders with customizable parameters.
- Supports basic authentication for secure API access.
- Handles JSON payloads and responses seamlessly.

## Installation

You can install the `kapital` package via pip. It's recommended to create a virtual environment for your project.

```bash
pip install kapital
```

## Usage

Here’s a quick guide on how to use the kapital client.

### Importing the Client

```python
from kapital import Kapital
```

### Initializing the Client

To use the client, initialize it with your credentials. If you don't provide any credentials, default values will be used.

```python
client = Kapital(
  base_url="https://e-commerce.kapitalbank.az/api",
  username="your-username",
  password="your-password"
)
```

### Creating a Payment Order

You can create a payment order by calling the `create_order` method. Here's an example:

```python
response = client.create_order(
  redirect_url="https://your-redirect-url.com",
  amount=100.00,
  description="Payment for Order #123",
  currency="AZN",
  language="az"
)

print(response)
```

### Response Structure

The `create_order` method returns a dictionary containing the following keys:

- `order_id`: The unique identifier for the order.
- `password`: The password for the order.
- `hppUrl`: The URL for redirecting the user to complete the payment.
- `status`: The status of the order.
- `cvv2AuthStatus`: The CVV2 authentication status.
- `secret`: A secret value associated with the order.
- `redirect_url`: The full URL to redirect the user for payment.

### Example Response

```python
{
  "order_id": "123456",
  "password": "secret_password",
  "hppUrl": "https://payment-url.com",
  "status": "pending",
  "cvv2AuthStatus": "approved",
  "secret": "order_secret",
  "redirect_url": "https://payment-url.com?id=123456&password=password"
}
```

## Saving a Card

To save a card for future transactions, use the `save_card` method:

```python
response, status_code = client.save_card(
  redirect_url="https://your-redirect-url.com",
  amount=100.0,
  description="Saving card for future use",
  currency="AZN",
  language="az",
)
```

In redirect url kapital will send a token which you can use for future transactions. The response will contain the token of the stored card.

```json
{
  "order": {
    "storedTokens": [
      {
        "id": "21790"
      }
    ]
  }
}
```

## Paying with a Stored Card

You can make a payment using a stored card by calling the `pay_with_card` method:

```python
response, status_code = client.pay_with_card(
  amount=100.0,
  description="Payment for services",
  token="21790",  # Replace with your stored card token
  currency="AZN",
  language="az",
)
```

## Refund a Transaction

To refund a transaction, use the `refund` method. Here's an example:

```python
response, status_code = client.refund(
  order_id="45451", # Replace with your order ID
  amount=100.0, # Amount to refund
)
```

## Reverse a Transaction

To reverse a transaction, call the `reverse` method:

```python
response, status_code = client.reverse(
  order_id="45451", # Replace with your order ID
)
```

## Get Order Details

You can retrieve the details of an order using the `get_order_details` method:

```python
response, status_code = client.get_order_details(
  order_id="45451", # Replace with your order ID
)
```

## Error Handling

The client raises exceptions for various error cases, such as:

- If the response status code is not 200, an Exception will be raised.
- If the response format is invalid, a ValueError will be raised indicating the specific issue.

```python
try:
  response = client.create_order(
    redirect_url="https://your-redirect-url.com",
    amount=100.00,
    description="Payment for Order #123"
  )
except Exception as e:
  print(f"An error occurred: {e}")
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or want to report bugs, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- [Zaman Kazimov](https://github.com/kazimovzaman2)
- [Fuad Huseynov](https://github.com/fuadhuseynov)

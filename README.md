# Notes Management API

This project is a RESTful API for managing notes, including user authentication, note creation, sentiment analysis integration, and WebSocket for real-time notifications and updates regarding note creations by users and subscribers. The API is built using Python, Flask, and MongoDB.

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Setup

### Clone the repository
```sh
git clone https://github.com/ElidorCohen/bigvu_backend.git
cd bigvu_backend
```

### Create and activate a virtual environment:
#### On Windows
```sh
python -m venv venv
venv\Scripts\activate
```
#### On macOS/Linux
```sh
python3 -m venv venv
source venv/bin/activate
```

### Install the dependencies:
```sh
pip install -r requirements.txt
```

### Run the application:
```sh
python run.py
```
##### The server will start on `http://127.0.0.1:3500`.

## Access the Swagger UI
#### The Swagger UI is accessible at http://127.0.0.1:3500/swagger.
To gain fully authenticated, execute the /login endpoint, copy the JWT that was returned.
Click the green button at the top right Swagger UI with text 'Authorize' and a lock icon.
Type: Bearer <token>
Click authorize and close buttons. Start executing authentication-required endpoints.

## Endpoints

### User Authentication
#### Register
- **Endpoint:** `POST /auth/register`
- **Description:**
  Creates a new user account in the system.
- **Body:** 
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

#### Login
- **Endpoint:** `POST /auth/login`
- **Description:**
  Authenticates a user and returns a JWT token for subsequent requests.
- **Body:** 
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

#### Profile
- **Endpoint:** `GET /auth/profile`
- **Description:**
  Retrieves the profile of the authenticated user.
- **Response:** 
  Contains username, user_id, and the latest sentiment analysis of the user's most recent note.

  

### Notes Management
#### Create Note
- **Endpoint:** `POST /notes/create_note`
- **Description:**
  Creates a new note for the authenticated user.
- **Body:** 
  ```json
  {
  "title": "string",
  "body": "string"
  }
  ```

#### Retrieve Notes
- **Endpoint:** `GET /notes/retrieve_notes`
- **Description:**
  Retrieves notes created by the authenticated user and users they are subscribed to.
- **Response:**  
  Contains list of notes of the user and the users which the user is subscribed to.


#### Retrieve Note By ID
- **Endpoint:** `GET /notes/{id}`
- **Description:**
  Retrieves a single note created by the authenticated user or by a user they are subscribed to.
- **Response:**  
  A single note object.



#### Subscribe
- **Endpoint:** `POST /subscribe/{id}`
- **Description:**
  Subscribe to a user's notes using the user's user_id. This allows an authenticated user to subscribe to another user's notes.
- **Body:** 
  ```json
  {
  "id": "string"
  }
  ```


#### List All Users
- **Endpoint:** `GET /users/`
- **Description:**
  A list of all users in the system. 
- **Response:**  
  A single note object. This can be used to find users to subscribe to.


## Sentiment Analysis Integration
The sentiment analysis is integrated with MeaningCloud Sentiment Analysis API. The API key can be found in the .env file. You can use your own API key or the one I used for the task.

## WebSocket Integration
I have integrated a system using WebSockets to allow users to receive real-time updates through the console, as there is no UI implementation; notifications are being broadcasted on the app's console. This setup provides notifications regarding note creations by users they are subscribed to. To ensure that subscribers receive these updates, I have created rooms identified by user_id. Subscribers need to listen to the specific room corresponding to the user_id to receive real-time notifications about new notes created by the user.

## Running Tests
### To run the tests, use the following command:
```sh
pytest -v --tb=short --disable-warnings -s tests
```

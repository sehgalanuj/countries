# Visited Countries Tracker

## Project Overview

The Visited Countries Tracker is a Flask-based web application that allows users to manage and track countries they have visited, with a focus on user-specific data. The application integrates geographical visualizations and user authentication, providing a personalized experience for each user. Admin features are included for user management.

## Features

- **User Authentication**: Supports login functionality and user sessions.
- **Country Management**: Users can mark countries they have visited and see these visually on a map.
- **Admin Panel**: Admins can add new users and view all registered users.
- **Geographical Data Visualization**: Integrates a GeoJSON map that highlights visited countries.

## File Structure

```
.
├── countries                     # Application code
│   ├── app.py                    # Main Flask application file
│   ├── countries.py              # Country management logic
│   ├── Dockerfile                # Dockerfile for building the application container
│   ├── requirements.txt          # Python dependencies
│   ├── static                    # Static files directory
│   │   └── custom.geo.json       # GeoJSON data for the map
│   └── templates                 # HTML templates for the application views
│       ├── admin.html            # Admin panel interface
│       ├── index.html            # Main user interface
│       └── login.html            # Login page
├── db                            # Directory for database file
│   └── countries.db              # SQLite database file
├── docker-compose.yml            # Docker Compose configuration file
└── README.md                     # Project documentation
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://your-repository-url.git
   cd your-repository-directory
   ```

2. **Build and Run the Application**

   Use Docker Compose to build and run the application:

   ```bash
   docker-compose up --build
   ```

   This command builds the Docker image and starts the application along with any necessary services. The application will be available at `http://localhost:5000`.

### Usage

- **Login Page**: Navigate to `http://localhost:5002` to access the login page.
- **Main Page**: Once logged in, the main page will display a map with countries marked as visited.
- **Admin Panel**: Admin users can access the admin panel via `http://localhost:5002/admin` to manage users.

## Development

### Adding New Dependencies

- To add new Python packages, update the `requirements.txt` file and rebuild the Docker image:

  ```bash
  docker-compose up --build
  ```

### Environment Variables

- You may configure environment variables in the `docker-compose.yml` file under the `environment` section for the service.

## Contributing

Contributions to the Visited Countries Tracker are welcome!

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is available under a Dual Licensing model:

- **Commercial Use**: For commercial use, this project requires a paid
    license. Fees and terms are available upon request. Please contact
    Anuj Sehgal <anuj@sehgal.eu> for more information about commercial
    licensing.
  
- **Non-commercial Use**: For non-commercial use, this project is
    licensed under the MIT License. This license permits personal use,
    development, testing, and non-commercial distribution, subject to
    the terms and conditions outlined in the license file.



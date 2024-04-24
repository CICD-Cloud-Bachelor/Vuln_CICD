## Dev

### Development Process

1. Clone the repository: `$ git clone https://github.com/your_username/your_app.git`
2. Install the required dependencies: `$ npm install`
3. Set up the database connection by updating the configuration file (`config.js`) with the appropriate credentials.
4. Run the database migration scripts to create the necessary tables: `$ npm run migrate`
5. Start the development server: `$ npm start`

### Database Structure

The app uses a relational database to store its data. Here is an overview of the database structure:

- **Table 1**: `users`
    - Columns: `id` (primary key), `name`, `email`, `password`

- **Table 2**: `posts`
    - Columns: `id` (primary key), `title`, `content`, `user_id` (foreign key referencing `users.id`)

### Usage

To use the app's database functionality, you can follow these steps:

1. Register a new user by providing a name, email, and password.
2. Log in with the registered credentials.
3. Create a new post by providing a title and content.
4. View all posts created by the logged-in user.
5. Edit or delete existing posts.

Remember to handle any potential errors or edge cases that may arise during the usage of the app.

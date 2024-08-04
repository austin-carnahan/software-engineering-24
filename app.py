import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from database import get_user_by_email, save_reset_token  # Import your functions

def create_app():
    app = Flask(__name__)

    # Load configuration
    config_name = os.getenv('FLASK_CONFIG', 'DevelopmentConfig')
    app.config.from_object(f'config.{config_name}')

    load_dotenv()  # Load environment variables from .env file

    CORS(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    # Initialize SendGrid client
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))

    # Import and register routes
    from routes.routes import register_routes
    register_routes(app)

    # Email sending route
    @app.route('/send-email', methods=['POST'])
    def send_email():
        data = request.get_json()
        from_email = Email("your_email@example.com")
        to_email = To(data['to'])
        subject = data['subject']
        content = Content("text/plain", data['body'])
        mail = Mail(from_email, to_email, subject, content)
        response = sg.send(mail)
        return jsonify({'status': 'email sent', 'response_code': response.status_code})

    @app.route('/forgot-password', methods=['POST'])
    def forgot_password():
        email = request.form['email']
        user = get_user_by_email(email)
        if user:
            reset_token = bcrypt.generate_password_hash(email + str(os.urandom(24))).decode('utf-8')
            save_reset_token(email, reset_token)
            reset_url = f'http://yourdomain.com/reset-password/{reset_token}'
            from_email = Email('your_email@example.com')
            to_email = To(email)
            subject = 'Password Reset Request'
            content = Content("text/html", f'Please click the following link to reset your password: <a href="{reset_url}">{reset_url}</a>')
            mail = Mail(from_email, to_email, subject, content)
            try:
                response = sg.send(mail)
                return jsonify({'message': 'Password reset email sent'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Email not found'}), 404

    @app.errorhandler(Exception)
    def handle_error(error):
        message = str(error)
        code = 500  # Internal Server Error

        if isinstance(error, KeyError):
            message = "Missing required data"
            code = 400  # Bad Request

        return jsonify({"error": message}), code

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

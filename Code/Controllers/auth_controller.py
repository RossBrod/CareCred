from typing import Dict, Optional
from flask import request, jsonify, session
from datetime import datetime
from ..Services.authentication_service import AuthenticationService, IdentityVerificationService, AuthorizationService
from ..Models.user import UserType


class AuthController:
    """Controller for authentication and authorization endpoints"""
    
    def __init__(self):
        self.auth_service = AuthenticationService()
        self.verification_service = IdentityVerificationService()
        self.authorization_service = AuthorizationService()
    
    def register_student(self):
        """POST /api/auth/register/student - Register new student"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['email', 'password', 'first_name', 'last_name', 'university', 'student_id']
            if not self._validate_required_fields(data, required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Register student
            result = self.auth_service.register_student(data)
            
            if result.success:
                return jsonify({
                    'success': True,
                    'user_id': result.user_id,
                    'message': 'Registration successful. Please check your email for verification.'
                }), 201
            else:
                return jsonify({'error': result.error_message}), 400
                
        except Exception as e:
            return jsonify({'error': 'Registration failed'}), 500
    
    def register_senior(self):
        """POST /api/auth/register/senior - Register new senior"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['email', 'password', 'first_name', 'last_name', 'age', 'address']
            if not self._validate_required_fields(data, required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Register senior
            result = self.auth_service.register_senior(data)
            
            if result.success:
                return jsonify({
                    'success': True,
                    'user_id': result.user_id,
                    'message': 'Registration successful. Admin approval required.'
                }), 201
            else:
                return jsonify({'error': result.error_message}), 400
                
        except Exception as e:
            return jsonify({'error': 'Registration failed'}), 500
    
    def login(self):
        """POST /api/auth/login - User login"""
        try:
            data = request.get_json()
            
            if not data.get('email') or not data.get('password'):
                return jsonify({'error': 'Email and password required'}), 400
            
            # Authenticate user
            result = self.auth_service.login(data['email'], data['password'])
            
            if result.success:
                # Set session
                session['user_id'] = result.user.user_id
                session['user_type'] = result.user.get_user_type().value
                
                return jsonify({
                    'success': True,
                    'access_token': result.access_token,
                    'refresh_token': result.refresh_token,
                    'user': {
                        'user_id': result.user.user_id,
                        'email': result.user.email,
                        'first_name': result.user.first_name,
                        'last_name': result.user.last_name,
                        'user_type': result.user.get_user_type().value,
                        'status': result.user.status.value
                    }
                }), 200
            else:
                return jsonify({'error': result.error_message}), 401
                
        except Exception as e:
            return jsonify({'error': 'Login failed'}), 500
    
    def logout(self):
        """POST /api/auth/logout - User logout"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            user_id = session.get('user_id')
            
            if user_id and token:
                self.auth_service.logout(user_id, token)
                session.clear()
            
            return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
            
        except Exception as e:
            return jsonify({'error': 'Logout failed'}), 500
    
    def refresh_token(self):
        """POST /api/auth/refresh - Refresh access token"""
        try:
            data = request.get_json()
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({'error': 'Refresh token required'}), 400
            
            result = self.auth_service.refresh_token(refresh_token)
            
            if result.success:
                return jsonify({
                    'access_token': result.access_token,
                    'expires_at': result.expires_at.isoformat()
                }), 200
            else:
                return jsonify({'error': 'Invalid refresh token'}), 401
                
        except Exception as e:
            return jsonify({'error': 'Token refresh failed'}), 500
    
    def verify_email(self):
        """GET /api/auth/verify-email?token=xxx - Verify email address"""
        try:
            token = request.args.get('token')
            
            if not token:
                return jsonify({'error': 'Verification token required'}), 400
            
            success = self.auth_service.verify_email(token)
            
            if success:
                return jsonify({'success': True, 'message': 'Email verified successfully'}), 200
            else:
                return jsonify({'error': 'Invalid or expired verification token'}), 400
                
        except Exception as e:
            return jsonify({'error': 'Email verification failed'}), 500
    
    def reset_password_request(self):
        """POST /api/auth/reset-password-request - Request password reset"""
        try:
            data = request.get_json()
            email = data.get('email')
            
            if not email:
                return jsonify({'error': 'Email required'}), 400
            
            success = self.auth_service.reset_password_request(email)
            
            # Always return success for security (don't reveal if email exists)
            return jsonify({
                'success': True, 
                'message': 'If email exists, reset instructions have been sent'
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Password reset request failed'}), 500
    
    def reset_password(self):
        """POST /api/auth/reset-password - Reset password with token"""
        try:
            data = request.get_json()
            token = data.get('token')
            new_password = data.get('new_password')
            
            if not token or not new_password:
                return jsonify({'error': 'Token and new password required'}), 400
            
            success = self.auth_service.reset_password(token, new_password)
            
            if success:
                return jsonify({'success': True, 'message': 'Password reset successfully'}), 200
            else:
                return jsonify({'error': 'Invalid or expired reset token'}), 400
                
        except Exception as e:
            return jsonify({'error': 'Password reset failed'}), 500
    
    def change_password(self):
        """POST /api/auth/change-password - Change password for authenticated user"""
        try:
            user_id = self._get_current_user_id()
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            data = request.get_json()
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            
            if not current_password or not new_password:
                return jsonify({'error': 'Current and new password required'}), 400
            
            success = self.auth_service.change_password(user_id, current_password, new_password)
            
            if success:
                return jsonify({'success': True, 'message': 'Password changed successfully'}), 200
            else:
                return jsonify({'error': 'Current password is incorrect'}), 400
                
        except Exception as e:
            return jsonify({'error': 'Password change failed'}), 500
    
    def submit_identity_verification(self):
        """POST /api/auth/identity-verification - Submit identity documents"""
        try:
            user_id = self._get_current_user_id()
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Handle file uploads and form data
            documents = self._process_uploaded_documents()
            
            verification_id = self.verification_service.submit_identity_documents(user_id, documents)
            
            return jsonify({
                'success': True,
                'verification_id': verification_id,
                'message': 'Documents submitted for verification'
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Document submission failed'}), 500
    
    def get_verification_status(self):
        """GET /api/auth/verification-status - Get identity verification status"""
        try:
            user_id = self._get_current_user_id()
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            status = self.verification_service.check_verification_status(user_id)
            
            return jsonify({'status': status}), 200
            
        except Exception as e:
            return jsonify({'error': 'Failed to get verification status'}), 500
    
    def _validate_required_fields(self, data: Dict, required_fields: list) -> bool:
        """Validate that all required fields are present in data"""
        return all(field in data and data[field] for field in required_fields)
    
    def _get_current_user_id(self) -> Optional[str]:
        """Get current authenticated user ID from session or token"""
        return session.get('user_id')
    
    def _process_uploaded_documents(self) -> Dict:
        """Process uploaded document files"""
        # Implementation would handle file uploads
        pass
    
    def _require_authentication(self):
        """Decorator to require authentication for endpoints"""
        pass
    
    def _require_permission(self, permission: str):
        """Decorator to require specific permission for endpoints"""
        pass
if password != confirm_password:
            return "Passwords do not match."
        
        if len(password) < 10:  
            return "Password must be at least 10 characters long."
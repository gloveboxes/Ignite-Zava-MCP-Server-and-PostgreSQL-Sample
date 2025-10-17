# Frontend Authentication Guide

## Overview

The management portal now uses real authentication with the backend API. Authentication is required for all `/api/management` endpoints.

## Authentication Flow

1. **Login**: User enters credentials on `/login` page
2. **Token Received**: Backend returns a JWT token and user info
3. **Token Storage**: Token is stored in `sessionStorage`
4. **Automatic Inclusion**: Token is automatically included in all management API requests via axios interceptor
5. **Session Persistence**: Token persists until user logs out or closes browser
6. **Auto Logout**: If token is invalid/expired (401 response), user is automatically logged out

## Test Credentials

### Admin User
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Can view and manage all stores

### Store Manager 1
- **Username**: `manager1`
- **Password**: `manager123`
- **Access**: Can only view/manage Store ID 1 (GitHub Popup NYC Times Square)

### Store Manager 2
- **Username**: `manager2`
- **Password**: `manager456`
- **Access**: Can only view/manage Store ID 2 (GitHub Popup SF Union Square)

## Implementation Details

### Auth Store (`src/stores/auth.js`)
- Handles login/logout
- Stores token and user info
- Provides `getToken()` method for retrieving current token

### Management Service (`src/services/management.js`)
- **Request Interceptor**: Automatically adds `Authorization: Bearer <token>` header to all requests
- **Response Interceptor**: Handles 401 errors by logging out user and redirecting to login

### Protected Endpoints
All management endpoints require authentication:
- `/api/management/dashboard/top-categories`
- `/api/management/suppliers`
- `/api/management/inventory`
- `/api/management/products`

### Role-Based Access Control

#### Admin Role
- Can access data from all stores
- Can filter by store using `?store_id=X` query parameter
- Sees aggregated data across all stores by default

#### Store Manager Role
- Automatically filtered to their assigned store only
- Cannot access other stores' data
- Any `store_id` parameter is ignored (always filtered to their store)

## API Response Format

### Login Success Response
```json
{
  "access_token": "abc123...",
  "token_type": "bearer",
  "user_role": "admin",
  "store_id": null,
  "store_name": null
}
```

### Login Error Response
```json
{
  "detail": "Invalid username or password"
}
```

### Protected Endpoint (401 Unauthorized)
```json
{
  "detail": "Invalid or expired token"
}
```

## Testing Authentication

### Manual Testing
1. Start the backend: `cd /workspace && uvicorn app.api.app:app --reload --host 0.0.0.0 --port 8091`
2. Start the frontend: `cd /workspace/frontend && npm run dev`
3. Navigate to `http://localhost:3000/login`
4. Try logging in with test credentials
5. Verify access to management pages
6. Try accessing another store's data (should be blocked for managers)

### Developer Notes

- Tokens are stored in `sessionStorage` (cleared on browser close)
- All management API calls automatically include the token
- 401 errors trigger automatic logout
- No need to manually add auth headers when using `managementService`

## Security Considerations

- Tokens are currently stored in sessionStorage (not localStorage)
- Tokens expire when browser is closed
- Invalid/expired tokens trigger immediate logout
- Store managers cannot bypass their store restrictions

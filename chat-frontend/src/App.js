import React, { useState } from "react";
import {
    BrowserRouter as Router,
    Route,
    Routes,
    Navigate,
} from "react-router-dom";
import Login from "./Login";
import Chat from "./Chat";

import "./App.css";

function App() {
    const [user, setUser] = useState(null);
    const [accessToken, setAccessToken] = useState("");

    const handleLogin = (userData, token) => {
        setUser(userData);
        setAccessToken(token);
    };

    return (
        <Router>
            <Routes>
                <Route
                    path="/login"
                    element={<Login onLogin={handleLogin} />}
                />
                <Route
                    path="/chat"
                    element={
                        user ? (
                            <Chat user={user} accessToken={accessToken} />
                        ) : (
                            <Navigate to="/login" />
                        )
                    }
                />
                <Route
                    path="/"
                    element={<Navigate to={user ? "/chat" : "/login"} />}
                />
            </Routes>
        </Router>
    );
}

export default App;

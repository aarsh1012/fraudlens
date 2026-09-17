import { createBrowserRouter } from "react-router"
import Login from "./features/auth/pages/Login"
import Register from "./features/auth/pages/Register"
import Protected from "./features/auth/components/protected"
import Home from "./features/urlcheck/pages/Home"
import History from "./features/urlcheck/pages/History"
import { UrlCheckProvider } from "./context/urlCheck.context"

export const router = createBrowserRouter([
    { path: "/login", element: <Login /> },
    { path: "/register", element: <Register /> },
    {
        path: "/",
        element: (
            <Protected>
                <UrlCheckProvider>
                    <Home />
                </UrlCheckProvider>
            </Protected>
        )
    },
    {
        path: "/history",
        element: (
            <Protected>
                <UrlCheckProvider>
                    <History />
                </UrlCheckProvider>
            </Protected>
        )
    },
])
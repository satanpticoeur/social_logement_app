import React from 'react';
import {Navbar} from "@/components/layout/Navbar.tsx";
import {Outlet} from "react-router-dom";

export const HomePage: React.FC = () => {
    return (
        <>
            <Navbar/>
            <div>
                <Outlet/>
            </div>

        </>
    );
};

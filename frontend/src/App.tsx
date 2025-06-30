import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import {Navbar} from './components/layout/Navbar';
import {HomePage} from './pages/HomePage';
import {UserListPage} from './pages/UserListPage';
import {RoomListPage} from "@/pages/RoomListPage.tsx";
import PaymentDashboardPage from "@/pages/PaymentDashboardPage.tsx";

function App() {
    return (
        <Router>
            <div className="">
                <Navbar/>

                <main className="container mx-auto p-4">
                    <Routes>
                        <Route path="/" element={<HomePage/>}/>
                        <Route path="/users" element={<UserListPage/>}/>
                        <Route path="/rooms" element={<RoomListPage/>}/>
                        <Route path="/payments" element={<PaymentDashboardPage />} />
                        {/*<Route path="/dashboard" element={<DashboardPage/>}/>*/}
                        {/*<Route path="/houses" element={<HousesPage/>}/>*/}
                        <Route path="*"
                               element={<h1 className="text-center text-3xl mt-10">404 - Page non trouvée</h1>}/>
                    </Routes>
                </main>
                {/* Un footer pourrait aller ici */}
            </div>
        </Router>
    );
}

export default App;
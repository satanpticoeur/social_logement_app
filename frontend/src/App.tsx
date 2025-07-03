import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import {Navbar} from './components/layout/Navbar';
import {HomePage} from './pages/HomePage';
import {UserListPage} from './pages/UserListPage';
import {RoomListPage} from "@/pages/RoomListPage.tsx";
import PaymentDashboardPage from "@/pages/PaymentDashboardPage.tsx";
import ContractListPage from "@/pages/contract/ContractListPage.tsx";
import ContractDetailPage from "@/pages/contract/ContractDetailPage.tsx";
import ContractEditPage from "@/pages/contract/ContractEditPage.tsx";
import ContractCreatePage from "@/pages/contract/ContractCreatePage.tsx";
import {AuthProvider} from "@/context/AuthContext.tsx";
import LoginPage from "@/pages/auth/LoginPage.tsx";
import RegisterPage from "@/pages/auth/RegisterPage.tsx";
import PrivateRoute from "@/components/PrivateRoute.tsx";

function App() {
    return (
        <Router>
            <AuthProvider>
                <Navbar/>
                <main className="container mx-auto p-4">
                    <Routes>
                        <Route path="/" element={<HomePage/>}/>
                        <Route path="/login" element={<LoginPage/>}/>
                        <Route path="/register" element={<RegisterPage/>}/>

                        {/* Routes protégées */}
                        <Route path="/users" element={<PrivateRoute> <UserListPage/> </PrivateRoute>}/>
                        <Route path="/rooms" element={<PrivateRoute> <RoomListPage/> </PrivateRoute>}/>
                        <Route path="/payments" element={<PrivateRoute> <PaymentDashboardPage/> </PrivateRoute>}/>
                        <Route path="/contracts" element={<PrivateRoute> <ContractListPage/> </PrivateRoute>}/>
                        <Route path="/contracts/:id" element={<PrivateRoute> <ContractDetailPage/> </PrivateRoute>}/>
                        <Route path="/contracts/:id/edit" element={<PrivateRoute> <ContractEditPage/> </PrivateRoute>}/>
                        <Route path="/contracts/create" element={<PrivateRoute> <ContractCreatePage/> </PrivateRoute>}/>
                        <Route path="/dashboard"
                               element={<PrivateRoute><h1 className="text-center text-3xl mt-10">Tableau de bord</h1>
                               </PrivateRoute>}/>
                        {/* Route 404 */}
                        <Route path="*"
                               element={<h1 className="text-center text-3xl mt-10"> 404 - Page non trouvée</h1>}/>


                    </Routes>
                </main>
            </AuthProvider>
        </Router>
    );
}

export default App;
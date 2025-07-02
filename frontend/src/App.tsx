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

function App() {
    return (
        <Router>
            <div>
                <Navbar/>

                <main className="container mx-auto p-4">
                    <Routes>
                        <Route path="/" element={<HomePage/>}/>
                        <Route path="/users" element={<UserListPage/>}/>
                        <Route path="/rooms" element={<RoomListPage/>}/>
                        <Route path="/payments" element={<PaymentDashboardPage />} />
                        <Route path="/contracts" element={<ContractListPage />} />
                        <Route path="/contracts/:id" element={<ContractDetailPage />} />
                        <Route path="/contracts/new" element={<ContractCreatePage />} />
                        <Route path="/contracts/:id/edit" element={<ContractEditPage />} />
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
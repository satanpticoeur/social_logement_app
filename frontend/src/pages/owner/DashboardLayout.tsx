import {AppSidebar} from "@/components/app-sidebar"
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import {Separator} from "@/components/ui/separator"
import {SidebarInset, SidebarProvider, SidebarTrigger,} from "@/components/ui/sidebar"
import {useEffect, useState} from 'react';
import {Outlet, useLocation, useNavigate} from 'react-router-dom';
import {toast} from "sonner";
import {ThemeToggle} from "@/components/theme/theme-toggle.tsx";
import {useAuth} from "@/context/AuthContext";


export default function DashboardLayoutPage() {
    const {user, isAuthenticated} = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState<boolean>(true);

    const location = useLocation();
    const currentPathname = location.pathname;

    useEffect(() => {
        if (!isAuthenticated || user?.role !== 'proprietaire') {
            toast.error("Accès refusé. Veuillez vous connecter en tant que propriétaire.");
            navigate('/');
            return;
        }
        setLoading(false);
    }, [isAuthenticated, user, navigate]);


    if (loading) {
        return <p>Chargement du tableau de bord...</p>;
    }

    return (
        <SidebarProvider>
            <AppSidebar/>
            <SidebarInset>
                <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
                    <SidebarTrigger className="-ml-1"/>
                    <Separator
                        orientation="vertical"
                        className="mr-2 data-[orientation=vertical]:h-4"
                    />
                    <Breadcrumb>
                        <BreadcrumbList>
                            {
                                currentPathname.split('/').filter(Boolean).map((segment, index, array) => {
                                    const isLast = index === array.length - 1;
                                    const path = `/${array.slice(0, index + 1).join('/')}`;

                                    return (
                                        <div className={"flex gap-3"} key={path}>
                                            <BreadcrumbItem>
                                                <BreadcrumbLink
                                                    asChild
                                                    className={isLast ? 'font-semibold' : ''}
                                                >
                                                    <BreadcrumbPage>
                                                        {segment.charAt(0).toUpperCase() + segment.slice(1)}
                                                    </BreadcrumbPage>
                                                </BreadcrumbLink>
                                            </BreadcrumbItem>
                                            {!isLast &&
                                                <BreadcrumbSeparator key={path + '-sep'}>/</BreadcrumbSeparator>}
                                        </div>
                                    );
                                })
                            }
                        </BreadcrumbList>
                    </Breadcrumb>
                    <div className="ml-auto">
                        <ThemeToggle/>
                    </div>

                </header>
                <div className="flex flex-1 flex-col gap-4">
                    <Outlet/>
                </div>
            </SidebarInset>
        </SidebarProvider>
    )
}

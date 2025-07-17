import * as React from "react"

import {NavMain} from "@/components/nav/nav-main.tsx"
import {NavUser} from "@/components/nav/nav-user.tsx"
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar"
import {
    BedDoubleIcon,
    HandCoinsIcon,
    HouseIcon,
    LayoutDashboardIcon,
    SignatureIcon,
    ListTodoIcon,
    UsersIcon
} from "lucide-react";

import {useAuth} from "@/context/AuthContext.tsx";
import {Link} from "react-router-dom";

const ownerNavMain = [
    {
        title: "Dashboard",
        url: "",
        icon: LayoutDashboardIcon,
    },
    {
        title: "Clients",
        url: "clients",
        icon: UsersIcon,
    },
    {
        title: "Chambres",
        url: "rooms",
        icon: BedDoubleIcon,
    }
    ,
    {
        title: "Maisons",
        url: "houses",
        icon: HouseIcon,
    },
    {
        title: "Contrats",
        url: "contracts",
        icon: SignatureIcon,
    },
    {
        title: "Demandes de location",
        url: "RentalRequests",
        icon: ListTodoIcon,
    },
    {
        title: "Paiements",
        url: "payments",
        icon: HandCoinsIcon,
    }
]
const lodgerNavMain = [
    {
        title: "Dashboard",
        url: "",
        icon: LayoutDashboardIcon,
    },
    {
        title: "Chambres",
        url: "rooms",
        icon: BedDoubleIcon,
    },
    {
        title: "Contrats",
        url: "contrats",
        icon: SignatureIcon,
    },
    {
        title: "Paiements",
        url: "paiements",
        icon: HandCoinsIcon,
    },
    {
        title: "Mes demandes",
        url: "mes-demandes",
        icon: ListTodoIcon,
    }
]


export function AppSidebar({...props}: React.ComponentProps<typeof Sidebar>) {
    const {user} = useAuth();
    return (
        <Sidebar collapsible="offcanvas" {...props}>
            <SidebarHeader>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton
                            asChild
                            className="data-[slot=sidebar-menu-button]:!p-1.5"
                        >
                            <Link to="dashboard">
                                <span className="text-base font-semibold">
                  Social Logment
                </span>
                            </Link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarHeader>
            <SidebarContent>
                <NavMain
                    items={user?.role === 'proprietaire' ? ownerNavMain : lodgerNavMain}
                />
            </SidebarContent>
            <SidebarFooter>
                <NavUser/>
            </SidebarFooter>
        </Sidebar>
    )
}

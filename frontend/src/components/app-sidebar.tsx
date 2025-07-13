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
import {BedDoubleIcon, HandCoinsIcon, HouseIcon, LayoutDashboardIcon, ListIcon, UsersIcon} from "lucide-react";

import {useAuth} from "@/context/AuthContext.tsx";

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
        icon: ListIcon,
    },
    {
        title: "Demandes de location",
        url: "RentalRequests",
        icon: UsersIcon,
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
        icon: ListIcon,
    },
    {
        title: "Paiements",
        url: "paiements",
        icon: HandCoinsIcon,
    },
    {
        title: "Mes demandes",
        url: "mes-demandes",
        icon: UsersIcon,
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
                            <a href="#">
                                <span className="text-base font-semibold">
                  Social Logment
                </span>
                            </a>
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

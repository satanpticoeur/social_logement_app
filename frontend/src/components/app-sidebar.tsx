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

const navMain = [
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
        title: "Paiements",
        url: "payments",
        icon: HandCoinsIcon,
    }
]


export function AppSidebar({...props}: React.ComponentProps<typeof Sidebar>) {
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
                <NavMain items={navMain}/>
            </SidebarContent>
            <SidebarFooter>
                <NavUser/>
            </SidebarFooter>
        </Sidebar>
    )
}

import {
    SidebarGroup,
    SidebarGroupContent,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar.tsx"
import {Link, useLocation} from "react-router-dom";
import {CirclePlusIcon} from "lucide-react";
import React from "react";

export function NavMain({items}: {
    items: {
        title: string
        url: string
        icon?: React.ComponentType<React.SVGProps<SVGSVGElement> | React.ComponentPropsWithoutRef<'svg'>>
    }[]
}) {

    const pathname = useLocation().pathname;
    const lastSegment = pathname.split('/').pop();
    return (
        <SidebarGroup>
            <SidebarGroupContent className="flex flex-col gap-2">
                <SidebarMenu>
                    <SidebarMenuItem className="flex items-center gap-2">
                        <SidebarMenuButton
                            tooltip="Quick Create"
                            className="bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground active:bg-primary/90 active:text-primary-foreground min-w-8 duration-200 ease-linear"
                        >
                            <CirclePlusIcon className="w-4 h-4"/>
                            <span>Gestion des locations</span>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
                <SidebarMenu>
                    {items.map((item) => (
                        <SidebarMenuItem key={item.title} className={
                                lastSegment === item.url.split('/').pop() ? 'bg-secondary text-secondary-foreground' : ''
                        }>
                            <Link to={item.url}>
                                <SidebarMenuButton tooltip={item.title}>
                                    {item.icon && <item.icon/>}
                                    <span>{item.title}</span>
                                </SidebarMenuButton>
                            </Link>
                        </SidebarMenuItem>
                    ))}
                </SidebarMenu>
            </SidebarGroupContent>
        </SidebarGroup>
    )
}

import {type Icon, IconCirclePlusFilled} from "@tabler/icons-react"

import {
    SidebarGroup,
    SidebarGroupContent,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar.tsx"
import {Link} from "react-router-dom";

export function NavMain({
                            items,
                        }: {
    items: {
        title: string
        url: string
        icon?: Icon | React.ComponentType<React.SVGProps<SVGSVGElement> | { size?: string | number }>;
    }[]
}) {

    return (
        <SidebarGroup>
            <SidebarGroupContent className="flex flex-col gap-2">
                <SidebarMenu>
                    <SidebarMenuItem className="flex items-center gap-2">
                        <SidebarMenuButton
                            tooltip="Quick Create"
                            className="bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground active:bg-primary/90 active:text-primary-foreground min-w-8 duration-200 ease-linear"
                        >
                            <IconCirclePlusFilled/>
                            <span>Gestion des locations</span>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
                <SidebarMenu>
                    {items.map((item) => (
                        <SidebarMenuItem key={item.title} className={
                            `/owner/dashboard/${item.url}` === window.location.pathname + '/' || `/owner/dashboard/${item.url}` === window.location.pathname ? 'bg-secondary text-secondary-foreground' : ''
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

import {BellIcon, LogOutIcon, UserCircleIcon} from "lucide-react"

import {Avatar, AvatarFallback, AvatarImage,} from "@/components/ui/avatar"
import {Button} from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent, DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {useAuth} from "@/context/AuthContext.tsx";


export default function UserMenu() {

    const {
        user,
        logout,
    } = useAuth();

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-auto p-0 hover:bg-transparent">
                    <Avatar>
                        <AvatarImage src="./avatar.jpg" alt="Profile image"/>
                        <AvatarFallback>
                            {user ? user.nom_utilisateur.charAt(0).toUpperCase() : "U"}
                            <span className="sr-only">
                    {user ? user.nom_utilisateur : "User Avatar"}
                </span>
                        </AvatarFallback>
                    </Avatar>
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="max-w-64" align="end">
                <DropdownMenuLabel className="flex min-w-0 flex-col">

                    <span className="text-foreground truncate text-sm font-medium">
                        {user ? user.email : "No email provided"}
                    </span>

                    <span className="text-muted-foreground truncate text-xs font-normal">
                        {user ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : "No role assigned"}
                    </span>
                </DropdownMenuLabel>
                <DropdownMenuSeparator/>

                <DropdownMenuGroup>
                    <DropdownMenuItem>
                        <UserCircleIcon size={16} className="opacity-60" aria-hidden="true"/>
                        <span>Mon profil</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                        <BellIcon size={16} className="opacity-60" aria-hidden="true"/>
                        <span>Notifications</span>
                    </DropdownMenuItem>
                </DropdownMenuGroup>


                <DropdownMenuSeparator/>
                <DropdownMenuItem
                    onClick={logout}>
                    <LogOutIcon size={16} className="opacity-60" aria-hidden="true"/>
                    <span>Déconnexion</span>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}

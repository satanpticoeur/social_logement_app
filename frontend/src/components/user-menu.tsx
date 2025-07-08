import {BoltIcon, BookOpenIcon, Layers2Icon, LogOutIcon, PinIcon, UserPenIcon,} from "lucide-react"

import {Avatar, AvatarFallback, AvatarImage,} from "@/components/ui/avatar"
import {Button} from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
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
                    {/*<span className="text-foreground truncate text-sm font-medium">*/}
                    {/*    {user ? user.nom_utilisateur : "Unknown User"}*/}
                    {/*</span>*/}

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
                        <BoltIcon size={16} className="opacity-60" aria-hidden="true"/>
                        <span>Option 1</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                        <Layers2Icon size={16} className="opacity-60" aria-hidden="true"/>
                        <span>Option 2</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                        <BookOpenIcon size={16} className="opacity-60" aria-hidden="true"/>
                        <span>Option 3</span>
                    </DropdownMenuItem>
                </DropdownMenuGroup>
                <DropdownMenuSeparator/>
                <DropdownMenuGroup>
                    <DropdownMenuItem>
                        <PinIcon size={16} className="opacity-60" aria-hidden="true"/>
                        <span>Option 4</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                        <UserPenIcon size={16} className="opacity-60" aria-hidden="true"/>
                        <span>Option 5</span>
                    </DropdownMenuItem>
                </DropdownMenuGroup>
                <DropdownMenuSeparator/>
                <DropdownMenuItem
                    onClick={logout}>
                    <LogOutIcon size={16} className="opacity-60" aria-hidden="true"/>
                    <span>Logout</span>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}

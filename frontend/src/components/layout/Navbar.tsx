import {
    BookUserIcon,
    DoorOpenIcon, HandCoinsIcon,
    HouseIcon, LayoutDashboardIcon, UsersIcon,
} from "lucide-react"

import Logo from "@/components/logo"
import {ThemeToggle} from "@/components/theme-toggle"
import UserMenu from "@/components/user-menu"
import {Button} from "@/components/ui/button"
import {
    NavigationMenu,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
} from "@/components/ui/navigation-menu"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"

import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip"
import {useAuth} from "@/context/AuthContext.tsx";
import {Link} from "react-router-dom";

// Navigation links with icons for desktop icon-only navigation
const navigationLinks = [
    {href: "/dashboard", label: "dashboard", icon: LayoutDashboardIcon, active: true},
    {href: "/users", label: "utilisateurs", icon: UsersIcon},
    {href: "/houses", label: "maisons", icon: HouseIcon},
    {href: "/rooms", label: "chambres", icon: DoorOpenIcon},
    {href: "/payments", label: "paiements", icon: HandCoinsIcon},
    {href: "/contracts", label: "contrats", icon: BookUserIcon},

]

export function Navbar() {
    const {isAuthenticated, isProprietaire} = useAuth();

    return (
        <header className="border-b px-4 md:px-6">
            <div className="flex h-16 items-center justify-between gap-4">
                {/* Left side */}
                <div className="flex flex-1 items-center gap-2">
                    {/* Mobile menu trigger */}
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button
                                className="group size-8 md:hidden"
                                variant="ghost"
                                size="icon"
                            >
                                <svg
                                    className="pointer-events-none"
                                    width={16}
                                    height={16}
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        d="M4 12L20 12"
                                        className="origin-center -translate-y-[7px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.1)] group-aria-expanded:translate-x-0 group-aria-expanded:translate-y-0 group-aria-expanded:rotate-[315deg]"
                                    />
                                    <path
                                        d="M4 12H20"
                                        className="origin-center transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.8)] group-aria-expanded:rotate-45"
                                    />
                                    <path
                                        d="M4 12H20"
                                        className="origin-center translate-y-[7px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.1)] group-aria-expanded:translate-y-0 group-aria-expanded:rotate-[135deg]"
                                    />
                                </svg>
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent align="start" className="w-36 p-1 md:hidden">
                            <NavigationMenu className="max-w-none *:w-full">
                                <NavigationMenuList className="flex-col items-start gap-0 md:gap-2">
                                    {navigationLinks.map((link, index) => {
                                        const Icon = link.icon
                                        return (
                                            <NavigationMenuItem key={index} className="w-full">
                                                <NavigationMenuLink
                                                    href={link.href}
                                                    className="flex-row items-center gap-2 py-1.5"
                                                    active={link.active}
                                                >
                                                    <Icon
                                                        size={16}
                                                        className="text-muted-foreground"
                                                        aria-hidden="true"
                                                    />
                                                    <span>{link.label}</span>
                                                </NavigationMenuLink>
                                            </NavigationMenuItem>
                                        )
                                    })}
                                </NavigationMenuList>
                            </NavigationMenu>
                        </PopoverContent>
                    </Popover>
                    <div className="flex items-center gap-6">
                        {/* Logo */}
                        <Link to="/" className="text-primary hover:text-primary/90">
                            <Logo/>
                        </Link>

                        {isAuthenticated &&
                            <>
                                {isProprietaire && <Link to="/contracts" className="hover:underline">Contrats</Link>}
                                {isProprietaire && <Link to="/clients" className="hover:underline">Clients</Link>}
                                <NavigationMenu className="hidden md:flex">
                                    <NavigationMenuList className="gap-2">
                                        <TooltipProvider>
                                            {navigationLinks.map((link) => (
                                                <NavigationMenuItem key={link.label}>
                                                    <Tooltip>
                                                        <TooltipTrigger asChild>
                                                            <NavigationMenuLink
                                                                href={link.href}
                                                                className="flex size-8 items-center justify-center p-1.5"
                                                            >
                                                                <link.icon size={20} aria-hidden="true"/>
                                                                <span className="sr-only">{link.label}</span>
                                                            </NavigationMenuLink>
                                                        </TooltipTrigger>
                                                        <TooltipContent
                                                            side="bottom"
                                                            className="px-2 py-1 text-xs"
                                                        >
                                                            <p>{link.label}</p>
                                                        </TooltipContent>
                                                    </Tooltip>
                                                </NavigationMenuItem>
                                            ))}
                                        </TooltipProvider>
                                    </NavigationMenuList>
                                </NavigationMenu>
                            </>
                        }


                        {/* Desktop navigation - icon only */}
                    </div>
                </div>

                {/* Right side */}
                <div className="flex items-center gap-2">
                    {/*si pas connecté */}

                    {!isAuthenticated && <>
                        <Link to="/login" className="hover:underline">Connexion</Link>
                        <Link to="/register" className="hover:underline">Inscription</Link>
                    </>
                    }
                    <ThemeToggle/>
                    {
                        isAuthenticated && <UserMenu/>
                    }
                </div>
            </div>
        </header>
    )
}

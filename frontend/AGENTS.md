# Frontend - Next.js Application

## Package Identity
Frontend is a Next.js 15 application that provides the user interface for the BettaFish multi-agent system. It features real-time agent monitoring, report visualization, and system configuration management with TypeScript and Tailwind CSS.

Primary tech/framework: Next.js 15 with React 19, TypeScript, Tailwind CSS, Prisma for database, and Socket.IO for real-time communication.

## Setup & Run
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Database operations
npm run db:push    # Push schema changes
npm run db:generate # Generate Prisma client
npm run db:migrate  # Run migrations
```

## Patterns & Conventions

### File Organization
- `src/app/` - Next.js App Router pages and API routes
- `src/components/` - Reusable React components
- `src/components/ui/` - UI components from shadcn/ui library
- `src/hooks/` - Custom React hooks
- `src/lib/` - Utility functions and configurations
- `prisma/` - Database schema and migrations
- `public/` - Static assets

### Component Architecture
✅ DO: Use shadcn/ui components with proper TypeScript:
```typescript
// Example from src/components/ui/button.tsx
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

❌ DON'T: Use unstyled components without proper TypeScript:
```typescript
// Avoid this pattern
function Button({ onClick, children }) {
  return <button onClick={onClick}>{children}</button>
}
```

### API Routes
✅ DO: Use Next.js App Router API routes with proper typing:
```typescript
// Example from src/app/api/engines/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const engineSchema = z.object({
  name: z.string(),
  status: z.enum(['starting', 'running', 'stopped']),
  port: z.number().optional()
})

export async function GET(request: NextRequest) {
  try {
    // Fetch engine status from backend
    const response = await fetch(`${process.env.BACKEND_URL}/api/status`)
    const data = await response.json()
    
    // Validate response
    const engines = engineSchema.array().parse(data)
    
    return NextResponse.json({ success: true, engines })
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to fetch engine status' },
      { status: 500 }
    )
  }
}
```

### Real-time Communication
✅ DO: Use Socket.IO for real-time updates:
```typescript
// Example from src/hooks/use-socket.ts
import { useEffect, useState } from 'react'
import { io, Socket } from 'socket.io-client'

export function useSocket(url: string) {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const socketInstance = io(url)
    
    socketInstance.on('connect', () => {
      setConnected(true)
    })
    
    socketInstance.on('disconnect', () => {
      setConnected(false)
    })
    
    setSocket(socketInstance)
    
    return () => {
      socketInstance.disconnect()
    }
  }, [url])

  return { socket, connected }
}
```

## Touch Points / Key Files

- Main layout: `src/app/layout.tsx` - Root layout with providers
- Homepage: `src/app/page.tsx` - Main dashboard
- Engine status: `src/app/api/engines/route.ts` - Engine status API
- System health: `src/app/api/system-health/route.ts` - Health check API
- Socket integration: `src/hooks/use-socket.ts` - Socket.IO hook
- Database schema: `prisma/schema.prisma` - Database model definitions
- UI components: `src/components/ui/` - Reusable UI components

## JIT Index Hints

- Find API routes: `rg -n "export.*function.*\(GET\|POST\)" src/app/api/`
- Find components: `rg -n "export.*function.*Component\|export.*const.*Component" src/components/`
- Find hooks: `rg -n "export.*function.*use\|export.*const.*use" src/hooks/`
- Find database models: `rg -n "model.*\{" prisma/schema.prisma`
- Find Socket.IO events: `rg -n "socket\.on\|socket\.emit" src/`
- Find UI components: `rg -n "export.*from.*@/components/ui" src/`

## Common Gotchas

- All API routes must handle errors and return proper status codes
- Socket.IO connections need proper cleanup in useEffect cleanup functions
- Database operations must use Prisma client with proper error handling
- Environment variables must be prefixed with NEXT_PUBLIC_ for client-side access
- TypeScript strict mode is enabled - all types must be properly defined
- Tailwind CSS classes must be properly configured in tailwind.config.ts

## Pre-PR Checks

```bash
# Type checking
npm run lint

# Build validation
npm run build

# Database schema validation
npm run db:generate

# Run tests (if available)
npm test
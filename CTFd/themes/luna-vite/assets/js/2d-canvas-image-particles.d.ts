declare module '2d-canvas-image-particles' {

    enum CursorMode {
        Bounce, Zoom, Light, Follow
    }

    enum RotationMode {
        None, Random, FollowVelocity
    }

    class Tint {
        constructor(hexColor: string, opacity: number);
    }

    interface ParticleSystemOptions {
        maxParticles?: number,
        velocityAngle?: [number, number],
        speed?: [number, number],
        rotationStartAngle?: [number, number],
        cursorMode?: CursorMode | null,     // (CursorMode.Bounce, CursorMode.Zoom, CursorMode.Light, CursorMode.Follow),
        rotationMode?: RotationMode, // (RotationMode.None, RotationMode.Random, RotationMode.FollowVelocity)
        rotationSpeed?: [number, number],
        rotationSpeedSizeScale?: number
        minimumRotationSpeed?: number // if min is negative and max is positive
        tints?: Tint[],
        width?: [number, number],
        height?: [number, number],
        addOnClickNb?: number,
        density?: number,
        cursorRadius?: number
    }

    class ParticleSystem {
        constructor(canvasId?: string | HTMLCanvasElement, imageUrl?: string, options?: ParticleSystemOptions);
        destroy(): void;
        static destroyAll(): void;
    }
}
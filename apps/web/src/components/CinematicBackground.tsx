import Image from "next/image";

export default function CinematicBackground() {
  return (
    <div
      className="fixed inset-0 z-0 pointer-events-none bg-graphite"
      aria-hidden="true"
    >
      {/* Static ground station background */}
      <div className="absolute inset-0">
        <div className="relative w-full h-full">
          <Image
            src="/hero_ground_station.jpg"
            alt="AfriGround ground station dish array"
            fill
            priority
            className="object-cover opacity-25"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-graphite/60 via-graphite/30 to-graphite" />
        </div>
      </div>

      {/* Readability film: fades content panels into the scene */}
      <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-graphite/60 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-72 bg-gradient-to-t from-graphite/80 to-transparent" />
    </div>
  );
}
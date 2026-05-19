"use client";

import Link from "next/link";
import { Play } from "lucide-react";

type GeneratedVideoCardData = {
  projectSlug: string;
  projectHeadline: string;
  productName: string;
  variantName: string;
  video?: string;
  cover?: string;
  duration?: number | null;
};

function mediaUrl(localPath?: string) {
  if (!localPath) return null;
  return `/api/media?path=${encodeURIComponent(localPath)}`;
}

export function GeneratedVideoCard({ video }: { video: GeneratedVideoCardData }) {
  const videoHref = mediaUrl(video.video) || "#";
  const coverHref = mediaUrl(video.cover);

  return (
    <article className="group overflow-hidden rounded-lg border border-ink/10 bg-white transition hover:-translate-y-0.5 hover:border-ink/25 hover:shadow-[0_18px_45px_rgba(31,46,43,0.08)]">
      <Link href={videoHref} className="relative block bg-[#202321]" target="_blank">
        {coverHref ? (
          // Plain img keeps local API media simple and avoids Next image domain rules.
          <img
            src={coverHref}
            alt={video.variantName}
            className="aspect-[9/16] w-full object-cover"
            onError={(event) => {
              event.currentTarget.style.display = "none";
              event.currentTarget.nextElementSibling?.classList.remove("hidden");
            }}
          />
        ) : null}
        <div className={coverHref ? "hidden" : ""}>
          <div className="grid aspect-[9/16] place-items-center px-6 text-center text-white/76">
            <div>
              <Play className="mx-auto h-8 w-8" />
              <div className="mt-4 text-sm font-semibold">Open video</div>
              <div className="mt-2 text-xs leading-5 text-white/48">Cover preview unavailable</div>
            </div>
          </div>
        </div>
      </Link>
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-ink/45">
              {video.productName}
            </div>
            <h3 className="mt-2 line-clamp-2 text-base font-semibold leading-snug text-ink">
              {video.variantName}
            </h3>
          </div>
          <span className="rounded-full border border-ink/10 px-2.5 py-1 text-xs text-ink/55">
            {video.duration ? `${video.duration}s` : "mp4"}
          </span>
        </div>
        <p className="mt-3 line-clamp-2 text-sm leading-6 text-ink/58">{video.projectHeadline}</p>
        <div className="mt-4 flex items-center justify-between gap-3 text-sm font-medium">
          <Link href={videoHref} className="underline underline-offset-4" target="_blank">
            Open video
          </Link>
          <Link href={`/projects/${video.projectSlug}`} className="text-ink/55 transition hover:text-ink">
            Project
          </Link>
        </div>
      </div>
    </article>
  );
}

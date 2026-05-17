import Link from "next/link";
import type { ReactNode } from "react";
import type { ProjectDetail } from "@/lib/repo-data";
import { Badge } from "@/components/ui/badge";
import { ButtonLink } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const steps = [
  {
    key: "overview",
    label: "Overview",
    href: "",
    description: "Project status and saved outputs"
  },
  {
    key: "reference",
    label: "Reference",
    href: "/reference",
    description: "Viral pattern card"
  },
  {
    key: "script",
    label: "Script",
    href: "/script",
    description: "Product script card"
  },
  {
    key: "assets",
    label: "Assets",
    href: "/assets",
    description: "Footage and shot plan"
  },
  {
    key: "render",
    label: "Render",
    href: "/render",
    description: "Worker, previews, delivery"
  }
] as const;

type StepKey = (typeof steps)[number]["key"];

function workflowHref(slug: string, suffix: string) {
  return `/projects/${slug}${suffix}`;
}

export function ProjectWorkflowShell({
  project,
  active,
  children
}: {
  project: ProjectDetail;
  active: StepKey;
  children: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-5">
      <Card>
        <CardContent className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="default">{project.productName}</Badge>
              <Badge>{project.status}</Badge>
              <Badge variant="outline">{project.workflowMode}</Badge>
            </div>
            <h2 className="mt-4 max-w-3xl text-3xl font-semibold leading-[1.05] tracking-[-0.05em] lg:text-5xl">
              {project.headline}
            </h2>
            <div className="mt-4 flex flex-wrap gap-4 text-sm text-black/60">
              <span>{project.name}</span>
              <span>{project.videoLength}</span>
              <span>{project.assetLibrary.assetCount} clips</span>
              <span>{project.deliverables.length} deliverables</span>
            </div>
          </div>
          <div className="flex gap-2">
            <ButtonLink href="/" variant="outline">
              All Projects
            </ButtonLink>
            <ButtonLink href={`/projects/${project.slug}/render`}>Run / Export</ButtonLink>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-3 lg:grid-cols-5">
        {steps.map((step, index) => {
          const isActive = active === step.key;
          return (
            <Link
              key={step.key}
              href={workflowHref(project.slug, step.href)}
              className={cn(
                "border p-4 transition",
                isActive ? "border-black bg-black text-white" : "border-black/10 bg-panel hover:border-black/30"
              )}
            >
              <div className={cn("font-mono text-[10px] uppercase tracking-[0.22em]", isActive ? "text-white/50" : "text-steel")}>
                {String(index).padStart(2, "0")}
              </div>
              <div className="mt-2 text-sm font-semibold">{step.label}</div>
              <div className={cn("mt-1 text-xs", isActive ? "text-white/58" : "text-black/50")}>{step.description}</div>
            </Link>
          );
        })}
      </div>

      {children}
    </div>
  );
}

export function DensePanel({
  title,
  description,
  children,
  className
}: {
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <Card className={cn("min-h-0", className)}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description ? <p className="mt-1 text-sm text-black/55">{description}</p> : null}
      </CardHeader>
      <CardContent className="min-h-0">{children}</CardContent>
    </Card>
  );
}

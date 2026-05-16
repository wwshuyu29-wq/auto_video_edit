import path from "path";

export const REPO_ROOT = path.resolve(process.cwd(), "../..");
export const PROJECTS_ROOT = path.join(REPO_ROOT, "projects");

export function projectFromSlug(slug: string) {
  const [group, ...rest] = slug.split("__");
  return { group, name: rest.join("__") };
}

export function projectDirFromSlug(slug: string) {
  const { group, name } = projectFromSlug(slug);
  return path.join(PROJECTS_ROOT, group, name);
}

export function slugFor(group: string, name: string) {
  return `${group}__${name}`;
}

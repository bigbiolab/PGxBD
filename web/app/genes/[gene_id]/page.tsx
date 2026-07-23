import { notFound } from "next/navigation";
import Link from "next/link";
import { getGeneDetail, getGenes } from "@/lib/api";
import Badge from "@/components/Badge";
import FrequencyBar from "@/components/FrequencyBar";
import { functionColor, cpicLevelColor } from "@/lib/colors";

// Static export has no per-request server, so every gene page must be
// enumerated at build time; unlisted ids fall through to app/not-found.tsx.
export const dynamicParams = false;

export async function generateStaticParams() {
  const genes = await getGenes();
  return genes.map((g) => ({ gene_id: g.gene_id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ gene_id: string }>;
}) {
  const { gene_id } = await params;
  return { title: `${gene_id} — PGxBD` };
}

export default async function GeneDetailPage({
  params,
}: {
  params: Promise<{ gene_id: string }>;
}) {
  const { gene_id } = await params;
  const detail = await getGeneDetail(gene_id);
  if (!detail) notFound();

  const { gene, star_alleles, beb_allele_frequencies, beb_phenotype_frequencies, drug_recommendations } =
    detail;

  return (
    <div className="flex flex-col gap-8">
      <div>
        <Link href="/genes" className="text-xs text-muted hover:text-accent">
          ← All genes
        </Link>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-semibold tracking-tight">{gene.gene_id}</h1>
          {gene.cpic_level && (
            <Badge color={cpicLevelColor(gene.cpic_level)}>CPIC {gene.cpic_level}</Badge>
          )}
          {gene.pharmvar_url && (
            <a
              href={gene.pharmvar_url}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-accent hover:underline"
            >
              PharmVar ↗
            </a>
          )}
        </div>
        <p className="mt-1 text-sm text-muted">
          {[gene.gene_name, gene.chromosome && `chr${gene.chromosome}`]
            .filter(Boolean)
            .join(" · ") || "—"}
        </p>
        {gene.function_category && (
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{gene.function_category}</p>
        )}
      </div>

      <section>
        <h2 className="text-sm font-semibold">
          Star alleles <span className="text-muted">({star_alleles.length})</span>
        </h2>
        <div className="mt-3 overflow-x-auto rounded-xl border border-border">
          <table className="w-full min-w-[480px] text-sm">
            <thead className="bg-surface-muted text-left text-xs text-muted">
              <tr>
                <th className="px-3 py-2 font-medium">Allele</th>
                <th className="px-3 py-2 font-medium">Function</th>
                <th className="px-3 py-2 font-medium">Defining variant(s)</th>
                <th className="px-3 py-2 font-medium">PharmVar ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {star_alleles.map((a) => (
                <tr key={a.allele_id} className="bg-surface">
                  <td className="px-3 py-2 font-medium">{a.star_allele}</td>
                  <td className="px-3 py-2">
                    {a.function ? (
                      <Badge color={functionColor(a.function)}>{a.function}</Badge>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-muted">{a.defining_variants || "—"}</td>
                  <td className="px-3 py-2 text-muted">{a.pharmvar_id || "—"}</td>
                </tr>
              ))}
              {star_alleles.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-3 py-4 text-center text-muted">
                    No star alleles on file for this gene.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold">
          BEB allele frequencies <span className="text-muted">({beb_allele_frequencies.length})</span>
        </h2>
        <div className="mt-3 overflow-x-auto rounded-xl border border-border">
          <table className="w-full min-w-[480px] text-sm">
            <thead className="bg-surface-muted text-left text-xs text-muted">
              <tr>
                <th className="px-3 py-2 font-medium">rsID</th>
                <th className="px-3 py-2 font-medium">Star allele</th>
                <th className="px-3 py-2 font-medium">Frequency (BEB)</th>
                <th className="px-3 py-2 font-medium">N</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {beb_allele_frequencies.map((f, i) => (
                <tr key={`${f.variant_rsid}-${i}`} className="bg-surface">
                  <td className="px-3 py-2 font-mono text-xs">{f.variant_rsid}</td>
                  <td className="px-3 py-2">{f.star_allele || "—"}</td>
                  <td className="px-3 py-2">
                    <FrequencyBar value={f.allele_frequency} population="BEB" />
                  </td>
                  <td className="px-3 py-2 text-muted">{f.sample_size ?? "—"}</td>
                </tr>
              ))}
              {beb_allele_frequencies.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-3 py-4 text-center text-muted">
                    No BEB allele frequency data for this gene.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold">
          BEB phenotype frequencies{" "}
          <span className="text-muted">({beb_phenotype_frequencies.length})</span>
        </h2>
        <div className="mt-3 flex flex-col gap-2 rounded-xl border border-border bg-surface p-4">
          {beb_phenotype_frequencies.map((p, i) => (
            <div key={`${p.phenotype}-${i}`} className="flex items-center gap-3">
              <span className="w-40 shrink-0 truncate text-sm">{p.phenotype}</span>
              <FrequencyBar value={p.frequency} population="BEB" />
            </div>
          ))}
          {beb_phenotype_frequencies.length === 0 && (
            <p className="text-sm text-muted">No BEB phenotype data for this gene.</p>
          )}
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold">
          Drug recommendations <span className="text-muted">({drug_recommendations.length})</span>
        </h2>
        <div className="mt-3 overflow-x-auto rounded-xl border border-border">
          <table className="w-full min-w-[640px] text-sm">
            <thead className="bg-surface-muted text-left text-xs text-muted">
              <tr>
                <th className="px-3 py-2 font-medium">Drug</th>
                <th className="px-3 py-2 font-medium">Phenotype</th>
                <th className="px-3 py-2 font-medium">Recommendation</th>
                <th className="px-3 py-2 font-medium">CPIC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {drug_recommendations.map((d, i) => (
                <tr key={`${d.drug_name}-${i}`} className="bg-surface align-top">
                  <td className="px-3 py-2 font-medium">{d.drug_name}</td>
                  <td className="px-3 py-2 text-muted">{d.phenotype}</td>
                  <td className="px-3 py-2 text-muted">{d.recommendation}</td>
                  <td className="px-3 py-2">
                    {d.cpic_level ? (
                      <Badge color={cpicLevelColor(d.cpic_level)}>{d.cpic_level}</Badge>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
              {drug_recommendations.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-3 py-4 text-center text-muted">
                    No drug recommendations on file for this gene.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

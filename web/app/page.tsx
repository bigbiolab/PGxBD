import Link from "next/link";
import { getApiInfo } from "@/lib/api";

export default async function HomePage() {
  const info = await getApiInfo();
  const s = info.statistics;

  return (
    <div className="flex flex-col gap-20">
      {/* Hero */}
      <section className="flex flex-col items-start gap-6 pt-6">
        <span className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-xs font-medium text-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" />
          Open pharmacogenomic database · v{info.version}
        </span>

        <h1 className="max-w-3xl text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
          Pharmacogenomic allele frequencies for the{" "}
          <span className="text-accent">Bangladeshi population</span>
        </h1>

        <p className="max-w-2xl text-base leading-7 text-muted">
          Bengali-in-Bangladesh (BEB) is largely absent from clinical pharmacogenomic
          reference data. PGxBD closes part of that gap: star-allele and phenotype
          frequencies for 29 key PGx variants across 18 pharmacogenes, computed under
          Hardy-Weinberg equilibrium from 1000 Genomes Project phase 3 whole-genome
          sequencing data (BEB, N=86) and benchmarked against 6 comparison populations.
        </p>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <Link
            href="/overview"
            className="rounded-lg bg-accent px-5 py-2.5 text-sm font-semibold text-accent-foreground transition-opacity hover:opacity-90"
          >
            Explore the database
          </Link>
          <Link
            href="/genes"
            className="rounded-lg border border-border bg-surface px-5 py-2.5 text-sm font-semibold transition-colors hover:border-accent hover:text-accent"
          >
            Browse genes
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="px-2 py-2.5 text-sm font-medium text-muted hover:text-accent"
          >
            API docs ↗
          </a>
        </div>

        <dl className="mt-4 flex flex-wrap gap-x-8 gap-y-3 border-t border-border pt-6 text-sm">
          <div>
            <dt className="text-muted">Pharmacogenes</dt>
            <dd className="text-lg font-semibold tabular-nums">{s.pharmacogenes}</dd>
          </div>
          <div>
            <dt className="text-muted">Allele frequencies</dt>
            <dd className="text-lg font-semibold tabular-nums">{s.allele_frequencies}</dd>
          </div>
          <div>
            <dt className="text-muted">Phenotype frequencies</dt>
            <dd className="text-lg font-semibold tabular-nums">{s.phenotype_frequencies}</dd>
          </div>
          <div>
            <dt className="text-muted">Drug recommendations</dt>
            <dd className="text-lg font-semibold tabular-nums">{s.drug_recommendations}</dd>
          </div>
          <div>
            <dt className="text-muted">Populations</dt>
            <dd className="text-lg font-semibold tabular-nums">7</dd>
          </div>
        </dl>
      </section>

      {/* Why */}
      <section>
        <h2 className="text-sm font-semibold">Why PGxBD</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-border bg-surface p-5">
            <h3 className="text-sm font-semibold">An underrepresented population</h3>
            <p className="mt-2 text-sm leading-6 text-muted">
              Most pharmacogenomic reference panels are built on European and East Asian
              cohorts. BEB (N=86, 1000 Genomes phase 3) is one of the few whole-genome
              datasets available for a South Asian / Bengali population.
            </p>
          </div>
          <div className="rounded-xl border border-border bg-surface p-5">
            <h3 className="text-sm font-semibold">Corrected &amp; validated</h3>
            <p className="mt-2 text-sm leading-6 text-muted">
              Seven correction rounds — strand-orientation flips, star-allele mislabels,
              chrX-aware hemizygous counting, missing HWE classes — cross-checked against
              CPIC and PharmVar, with an automated validation suite on every build.
            </p>
          </div>
          <div className="rounded-xl border border-border bg-surface p-5">
            <h3 className="text-sm font-semibold">Open REST API</h3>
            <p className="mt-2 text-sm leading-6 text-muted">
              Every table — genes, star alleles, frequencies, phenotypes, drug
              recommendations — is queryable over a documented FastAPI service. This UI
              is just one client of it.
            </p>
          </div>
        </div>
      </section>

      {/* Data sources */}
      <section>
        <h2 className="text-sm font-semibold">Data sources</h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {[
            "1000 Genomes Project (phase 3, GRCh37)",
            "PharmGKB",
            "CPIC",
            "PyPGx",
            "dbSNP",
          ].map((src) => (
            <span
              key={src}
              className="rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-muted"
            >
              {src}
            </span>
          ))}
        </div>
      </section>

      {/* CTA banner */}
      <section className="flex flex-col items-start gap-3 rounded-2xl border border-border bg-surface-muted p-8 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Ready to explore the data?</h2>
          <p className="mt-1 text-sm text-muted">
            Query allele frequencies, phenotypes, and drug recommendations across 7
            populations.
          </p>
        </div>
        <Link
          href="/overview"
          className="shrink-0 rounded-lg bg-accent px-5 py-2.5 text-sm font-semibold text-accent-foreground transition-opacity hover:opacity-90"
        >
          Open the database
        </Link>
      </section>
    </div>
  );
}

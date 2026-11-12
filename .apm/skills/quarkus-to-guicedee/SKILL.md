---
name: quarkus-to-guicedee
description: Migrate a Quarkus application to GuicedEE, first setting up the GuicedEE APM marketplace and relevant framework skills, then replacing Quarkus facilities with Guice injection, GuicedEE lifecycle and reactive Vert.x integrations.
---

# Quarkus to Guiced

Read [provenance and evidence](references/provenance.md). Preserve GuicedEE's Guice-based, reactive architecture; this is not a migration to a traditional CDI application server.

Start with [marketplace setup](references/setup.md) in the consuming application. Verify the GuicedEE marketplace identity and revision, install the retrofit and runtime skills for the selected assistant, and read their current instructions. Select additional modules from the actual Quarkus extension inventory. Installing this migration skill alone does not automatically install another marketplace or its packages.

Inventory source versions, extensions, CDI scopes/producers/interceptors, REST/routes, event consumers, configuration, security, persistence and packaging. Establish baseline tests and contracts. Use [replacement decisions](references/migration.md) to map each facility before deleting it; preserve unrelated work.

Apply guicedee-installer to existing modules and guicedee-creator only for new modules. Follow the selected release's Maven/JDK/BOM and JPMS requirements; verify inherited settings through the effective POM. Do not copy stale example versions or mix Quarkus-managed Vert.x with GuicedEE-managed dependencies.

Use guicedee-inject and guicedee-client for module registration, Guice binding and asynchronous lifecycle. Dual-register SPIs for JPMS and classpath operation. Use guicedee-vertx for managed runtime/event consumers, and web/REST skills as needed. Await loading completion before readiness. Do not create a second application Vert.x runtime to work around injection failures.

Migrate one vertical slice at a time and run [acceptance checks](references/verification.md). Preserve request/call-scope isolation, nonblocking execution, authentication, authorization, validation and transaction boundaries. Quarkus annotations and Panache APIs require explicit replacements; removing them does not reproduce their behaviour. Never disable security or tests to make a migration pass.

Remove Quarkus runtime, augmentation, plugins and test harness dependencies only after replacements pass. Keep production deployment and data migration separate. Report exact marketplace/package/runtime revisions, changes, baseline and target evidence, unresolved incompatibilities and unperformed checks. Marketplace installation, static validation, compilation and production acceptance are distinct results.

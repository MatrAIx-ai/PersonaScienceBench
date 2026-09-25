# EXP-Bench execution boundaries

The supported experiment here is the design-only workflow described in the [adapter guide](../adapters/expbench.md). The actor inspects public inputs, discusses its approach, writes a design and reviews its evidence with the simulator. The sealed design is evaluated separately.

The runner can generate a minimal public workspace automatically. Optional repository staging and full-workflow continuation remain separate modes; they are not included in the reported coverage scores. Use fresh output paths and keep every failure/recovery record locally.

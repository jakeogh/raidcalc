```
$ raidcalc --help
Usage: raidcalc [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  --help  Show this message and exit.

Commands:
  define
  mirror
  stripe
  z1
  z2
  z3

$ # define a 4x 5TB array, split it into 2x mirrors and stripe them
$ raidcalc define 5 4 mirror 2 stripe all
ic| define: [5, 5, 5, 5]
ic| mirrored: [5, 5]
ic| striped: [10]

$ # define a 16x 5TB array, split it into 2x RAIZz3 groups and stripe them:
$ raidcalc define 5 16 z3 split stripe all
ic| define: [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
ic| raidz3: [25, 25]
ic| striped: [50]

$ # see grouping steps:
$ raidcalc define --verbose 5 16 z3 split stripe all
ic| define: [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
ic| grouped: [(5, 5, 5, 5, 5, 5, 5, 5), (5, 5, 5, 5, 5, 5, 5, 5)]
ic| raidz3: [25, 25]
ic| grouped: [(25, 25)]
ic| striped: [50]

$ # define a 16x 5TB array, split it into 4x RAIZz2 groups and RAIZz1 them:
$ raidcalc define --verbose 5 16 z2 4 z1 all
ic| define: [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
ic| grouped: [(5, 5, 5, 5), (5, 5, 5, 5), (5, 5, 5, 5), (5, 5, 5, 5)]
ic| raidz2: [10, 10, 10, 10]
ic| grouped: [(10, 10, 10, 10)]
ic| raidz1: [30]

```

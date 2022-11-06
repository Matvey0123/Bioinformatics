import os
from typing import Tuple

import flytekit
from flytekit import kwtypes, task, workflow
from flytekit.extras.tasks.shell import OutputLocation, ShellTask
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile

t1 = ShellTask(
    name="task_1",
    debug=True,
    script="""
    gzip -d {inputs.genom}
    bwa index genom.fna

    bwa mem genom.fna {inputs.ecoli} > aln.sam

    samtools view -S -b aln.sam > aln.bam
    samtools flagstat aln.sam > aln.txt

    percent=`grep "[0-9] mapped" aln.txt | awk ' {print $5} ' | sed 's/(//'| sed 's/%//'`
    control=90.0

    if [ 1 -eq "$(echo "${percent} < ${control}" | bc)" ] 
    then
	    echo "not OK"
    else
	    echo "OK"
	    samtools sort aln.bam -o aln.sorted.bam
	    freebayes -f genom.fna aln.sorted.bam > results.vcf
    fi
    """,
    inputs=kwtypes(ecoli=FlyteFile, genom=FlyteFile),
    output_locs=[OutputLocation(var="i", var_type=FlyteFile, location="results.vcf")],
)

@task
def initial_files() -> Tuple[FlyteFile, FlyteFile]:
    working_dir = flytekit.current_context().working_directory
    ecoli = os.path.join(working_dir, "ecoli.fastq.gz")
    genom = os.path.join(working_dir, "genom.fna.gz")
    return ecoli, genom

@workflow
def wf() -> FlyteFile:
    ecoli, genom = initial_files()
    results = t1(ecoli=ecoli, genom=genom)
    return results

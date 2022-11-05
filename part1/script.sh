#!/bin/bash

mkdir fastqcout
fastqc -f fastq -o fastqcout/ ecoli.fastq.gz
cd fastqcout/
unzip ecoli_fastqc.zip
cd ecoli_fastqc/
mv fastqc_report.html ../..
cd ../..

gzip -d genom.fna.gz
bwa index genom.fna

bwa mem genom.fna ecoli.fastq.gz > aln.sam

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
rm -rf *.bam *.sam *.sorted.bam *.txt *.html *.fna.* *.vcf fastqcout/
gzip genom.fna


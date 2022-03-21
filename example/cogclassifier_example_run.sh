mkdir ./output

# Run COGclassifier for 3 species example dataset
COGclassifier -i ./input/ecoli.faa -o ./output/ecoli_cog_classifier
COGclassifier -i ./input/synechocystis.faa -o ./output/synechocystis_cog_classifier
COGclassifier -i ./input/mycoplasma.faa -o ./output/mycoplasma_cog_classifier

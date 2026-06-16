#!/usr/bin/R Rscript


getwd()

library(gprofiler2)
library(tidyr)
library(dplyr)
library(stringr)
library(readr)

get_version_info(organism = "athaliana")
print(get_version_info(organism = "athaliana"))
#other species - "osativa", "sbicolor", "tarefseqv2", "tturgidum", "hvulgare", "zmays", and "bdistachyon"

input <- read.delim("drought_genes.txt", header=FALSE)
head(input)
str(input)

at_gene_list <- input[grep("^AT", input$V1), ] 
print(at_gene_list)

at_gene_list <- unique(at_gene_list)
print(at_gene_list)

gostres <- gost(query = at_gene_list,
                organism = "athaliana", ordered_query = FALSE,
                multi_query = FALSE, significant = TRUE, exclude_iea = FALSE,
                measure_underrepresentation = FALSE, evcodes = TRUE, #evcodes-this adds a column to the output called intersection, which contains gene IDs associated with each enriched term.
                user_threshold = 0.05, correction_method = "g_SCS",
                domain_scope = "annotated", custom_bg = NULL,
                numeric_ns = "", sources = NULL, as_short_link = FALSE, highlight = TRUE)

names(gostres)
head(gostres$result, 3)
print(gostres$result)

head(gostres$meta, 3)
print(gostres$meta)

result_table <- gostres$result %>%
  select(term_id, term_name, intersection, p_value, source, significant) %>%
  mutate(gene_id = str_split(intersection, ",")) %>%
  unnest(gene_id) %>%
  mutate(gene_id = str_trim(gene_id))  # remove any whitespace

# Get all genes that were annotated with at least one GO term
annotated_genes <- gostres$result %>%
  pull(intersection) %>%
  str_split(",") %>%
  unlist() %>%
  str_trim() %>%
  unique()

# Find which genes got GO terms
genes_with_go <- intersect(at_gene_list, annotated_genes)
print(genes_with_go)

# Find which genes did not get annotated
genes_without_go <- setdiff(at_gene_list, annotated_genes)
print(genes_without_go)

# Print counts
cat("Total input genes:", length(at_gene_list), "\n")
cat("Annotated with GO terms:", length(genes_with_go), "\n")
cat("Not annotated:", length(genes_without_go), "\n")
cat("Not annotated:", genes_without_go, "\n")

write.csv(result_table, file="result_table_athaliana.csv")

go_data <- read_csv("result_table_athaliana.csv")

# Summarize to one row per GO term
go_summary <- go_data %>%
  group_by(term_id, term_name, p_value) %>%
  summarise(gene_count = n(), .groups = "drop")  # counts how many gene rows per term

# View it
head(go_summary)

library(ggplot2)

ggplot(go_summary, aes(
  x = reorder(term_name, -log10(p_value)),
  y = -log10(p_value),
  size = gene_count,
  color = p_value
)) +
  geom_point(alpha = 0.8) +
  coord_flip() +
  scale_color_gradient(low = "red", high = "blue", trans = "log") +
  labs(
    x = "GO Term",
    y = "-log10(p-value)",
    size = "Gene Count",
    color = "p-value"
  ) +
  theme_minimal()
ggsave("go_enrichment_dotplot_athaliana.pdf", width = 20, height = 30, dpi = 1800)

top_go <- go_summary %>%
  arrange(p_value) %>%
  slice(1:20)

#plot the top20 terms
ggplot(top_go, aes(
  x = reorder(term_name, -log10(p_value)),
  y = -log10(p_value),
  size = gene_count,
  color = p_value
)) +
  geom_point(alpha = 0.8) +
  coord_flip() +
  scale_color_gradient(low = "red", high = "blue", trans = "log") +
  labs(
    x = "GO Term",
    y = "-log10(p-value)",
    size = "Gene Count",
    color = "p-value"
  ) +
  theme_minimal()
ggsave("go_enrichment_dotplot_athaliana1.png", width = 7, height = 5, dpi = 1900)

sessionInfo()



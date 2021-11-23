library(tidyverse)

## DATA
base_url<-"https://media.githubusercontent.com"
path_url<- "/media/Shampjeff/OCA/main/pretrial.csv"
df<- read.csv(paste0(base_url,path_url))

### Organize data frames
five_boros<-c("new york", "kings", "queens", "richmond", "bronx")
df<- 
  df %>%
  filter(bail_set_and_posted_at_arraign == "y"|
           bail_set_and_not_posted_at_arraign == "y") %>%
  filter(county_name %in% five_boros)

top_arraign_char<-
  df %>%
  select(top_arraign_article_section) %>%
  unique()

bail_df<-
  df %>%
  filter(top_arraign_article_section %in% top_arraign_char$top_arraign_article_section) %>%
  filter(dollar_bail_bxd == "False")


##LIST selectors
## Charge List
top_arraign_char<- top_arraign_char$top_arraign_article_section

top_charge_counts_df<-
  df %>%
  filter(top_arraign_article_section %in% top_arraign_char) %>%
  select(top_charge_at_arraign) %>%
  group_by(top_charge_at_arraign) %>%
  summarise(count_charge = n()) %>%
  arrange(desc(count_charge))


### Judge Names; most and least common
most_common_judge_vec<-
  bail_df %>%
  group_by(judge_name) %>%
  summarise(judge_count = n()) %>%
  filter(judge_count >= 50) %>%
  arrange(desc(judge_count)) %>%
  select(judge_name)

less_common_judge_vec<-
  bail_df %>%
  group_by(judge_name) %>%
  summarise(judge_count = n()) %>%
  filter(judge_count <= 50) %>%
  arrange(desc(judge_count)) %>%
  select(judge_name)

all_judge_vec<-
  bail_df %>%
  group_by(judge_name) %>%
  summarise(judge_count = n()) %>%
  arrange(desc(judge_count)) %>%
  select(judge_name)

### MOST and LEAST Common Judge names
most_common_judge_vec <- most_common_judge_vec$judge_name
less_common_judge_vec<- less_common_judge_vec$judge_name
all_judge_vec<- all_judge_vec$judge_name







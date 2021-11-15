library(shiny)
library(tidyverse)


df<- read.csv("pretrial.csv")
df %>%
  select(bail_set_and_posted_at_arraign == "Y", 
         bail_set_and_not_posted_at_arraign == "Y")
#### SERVER FUNCTIONS ####
library(shiny)
library(tidyverse)

server <- function(input, output) {
  
  output$description<- renderText({"Charge Description:"})
  output$description_2<- renderText({"Charge Description:"})
  
  output$text<- renderText({
    test<- 
      top_charge_counts_df %>%
      filter(str_detect(top_charge_at_arraign, input$article_section)) %>%
      filter(row_number() == 1)
    test$top_charge_at_arraign
  })
  
  output$text_2<- renderText({
    test_2<- 
      top_charge_counts_df %>%
      filter(str_detect(top_charge_at_arraign, input$article_section_2)) %>%
      filter(row_number() == 1)
    test_2$top_charge_at_arraign
  })
  
  output$bail_time<- renderPlot({
    
    bail_yrange<- 
      bail_df %>% 
      filter(top_arrest_article_section == input$article_section)
    bail_yrange<- range(bail_yrange$first_bail_set_cash, na.rm=TRUE)
    
    median_bail<- 
      bail_df %>%
      filter(top_arrest_article_section == input$article_section) %>%
      select(first_bail_set_cash) %>%
      summarise(median_bail = median(first_bail_set_cash, na.rm=TRUE))
    
    bail_df %>%
      filter(top_arrest_article_section == input$article_section) %>%
      ggplot(aes(x=first_arraign_date, y=first_bail_set_cash)) +
      geom_boxplot() +
      scale_y_log10(n.breaks=10) +
      geom_hline(yintercept = median_bail$median_bail,
                 color='red3', alpha=0.5) +
      annotate('text', x="2020-06-01",
               y=max(bail_yrange),
               label=paste0("median bail: ",
                            median_bail$median_bail),
               color="red3") +
      labs(title="Cash Bail Distributions by Month", 
           x="Month of Arraignment",
           y="Cash Bail Amount",
           subtitle = paste0("Article Section: ",input$article_section,"  ")
           ) +
      theme(axis.text.x = element_text(angle = 90, vjust = 0.0, hjust=0))
    
  }, height = 400, width = 800)
  
  
  output$bail_histo_race<- renderPlot({

    bail_df %>%
      filter(top_arrest_article_section == input$article_section) %>%
      filter(race %in% c("black", "white"),
             ethnicity %in% c("hispanic", "non hispanic")) %>%
      ggplot(aes(x=first_bail_set_cash)) +
      geom_histogram(position = "dodge") +
      scale_x_log10(n.breaks=10) +
      facet_grid(~race ~ ethnicity) +
      labs(title="Frequency of Cash Bail Amount by Race and Ethnicity", 
           x="Cash Bail Amount",
           y="Frequency"
      ) +
      theme(legend.position = "None",
            axis.text.x = element_text(angle = 90, vjust = 0.0, hjust=0))
    
  }, height = 400, width = 800)

  output$bail_by_priors<- renderPlot({
    
    bail_df %>%
      filter(top_arrest_article_section == input$article_section) %>%
      filter(race %in% c("black", "white")) %>%
      filter(ethnicity %in% c("hispanic", "non hispanic")) %>%
      ggplot(aes(x=factor(priors_sum_bxd), y=first_bail_set_cash)) +
      geom_boxplot() +
      scale_y_log10() +
      facet_grid(~race ~ethnicity) +
      labs(title="Cash Bail Distributions by Number of Prior Convictions", 
           x="Number of Prior Convictions",
           y="Cash Bail Amount")
    
  }, height = 500, width = 800)
  
  output$judge_least<- renderPlot({
    
    bail_yrange_2<- 
      bail_df %>% 
      filter(top_arrest_article_section == input$article_section_2)
    bail_yrange_2<- range(bail_yrange_2$first_bail_set_cash, na.rm=TRUE)
    
    median_bail_least<- 
      bail_df %>%
      filter(top_arrest_article_section == input$article_section_2) %>%
      filter(judge_name %in% less_common_judge_vec) %>%
      select(first_bail_set_cash) %>%
      summarise(median_bail_least = median(first_bail_set_cash, na.rm=TRUE))
    
    bail_df %>%
      filter(judge_name %in% less_common_judge_vec) %>%
      filter(top_arrest_article_section == input$article_section_2) %>%
      ggplot(aes(x=first_arraign_date, y=first_bail_set_cash)) +
      geom_boxplot() +
      scale_y_log10(n.breaks=10) +
      geom_hline(yintercept = median_bail_least$median_bail_least,
                 color='red3', alpha=0.5) +
      annotate('text', x="2020-06-01",
               y=max(bail_yrange_2),
               label=paste0("median bail: ",median_bail_least$median_bail_least),
               color="red3") +
      labs(title= "Cash Bail Distribution for Less Common Judges",
           x="Month of Arraignment",
           y="Cash Bail Set") +
      theme(axis.text.x = element_text(angle = 90, vjust = 0.0, hjust=0))
    
  },height = 400, width = 800)
  
  output$judge_most<- renderPlot({
    
    bail_yrange_2<- 
      bail_df %>% 
      filter(top_arrest_article_section == input$article_section_2)
    bail_yrange_2<- range(bail_yrange_2$first_bail_set_cash, na.rm=TRUE)
    
    median_bail_most<- 
      bail_df %>%
      filter(top_arrest_article_section == input$article_section_2) %>%
      filter(judge_name %in% most_common_judge_vec) %>%
      select(first_bail_set_cash) %>%
      summarise(median_bail_most = median(first_bail_set_cash, na.rm=TRUE))
    
    bail_df %>%
      filter(judge_name %in% most_common_judge_vec) %>%
      filter(top_arrest_article_section == input$article_section_2) %>%
      ggplot(aes(x=first_arraign_date, y=first_bail_set_cash)) +
      geom_boxplot() +
      scale_y_log10(n.breaks=10) +
      geom_hline(yintercept = median_bail_most$median_bail_most,
                 color='red3', alpha=0.5) +
      annotate('text', x="2020-06-01",
               y=max(bail_yrange_2),
               label=paste0("median bail: ",
                            median_bail_most$median_bail_most),
               color="red3") +
      labs(title= "Cash Bail Distribution for More Common Judges",
           x="Month of Arraignment",
           y="Cash Bail Set") +
      theme(axis.text.x = element_text(angle = 90, vjust = 0.0, hjust=0))
    
  }, height = 400, width = 800)
  
  output$histo_most<- renderPlot({
    
    median_bail_most<- 
      bail_df %>%
      filter(top_arrest_article_section == input$article_section_2) %>%
      filter(judge_name %in% most_common_judge_vec) %>%
      select(first_bail_set_cash) %>%
      summarise(median_bail_most = median(first_bail_set_cash, na.rm=TRUE))
    
    bail_df %>%
      filter(judge_name %in% most_common_judge_vec) %>%
      filter(top_arrest_article_section == input$article_section_2) %>%
      filter(race %in% c("black", "white"),
             ethnicity %in% c("hispanic", "non hispanic")) %>%
      ggplot(aes(x=first_bail_set_cash, fill=ethnicity)) +
      geom_histogram(position = "dodge") +
      scale_x_log10() +
      facet_grid(~race ~ ethnicity) +
      labs(title= "Frequency of Bail Amount for More Common Judges",
           x="Cash Bail Amount",
           y="Frequency") +
      theme(legend.position = "none",
            axis.text.x = element_text(angle = 90, vjust = 0.0, hjust=0))
    
    }, height = 400, width = 400)
  
  output$histo_least<- renderPlot({

    median_bail_least<-
      bail_df %>%
      filter(top_arrest_article_section == input$article_section_2) %>%
      filter(judge_name %in% less_common_judge_vec) %>%
      select(first_bail_set_cash) %>%
      summarise(median_bail_least = median(first_bail_set_cash, na.rm=TRUE))

    bail_df %>%
      filter(judge_name %in% less_common_judge_vec) %>%
      filter(top_arrest_article_section == input$article_section_2) %>%
      filter(race %in% c("black", "white"),
             ethnicity %in% c("hispanic", "non hispanic")) %>%
      ggplot(aes(x=first_bail_set_cash, fill=ethnicity)) +
      geom_histogram(position = "dodge") +
      scale_x_log10() +
      facet_grid(~race ~ ethnicity) +
      labs(title= "Frequency of Bail Amount for Less Common Judges",
           x="Cash Bail Amount",
           y="Frequency") +
      theme(legend.position="none", 
            axis.text.x = element_text(angle = 90, vjust = 0.0, hjust=0))

  }, height = 400, width = 400)

  output$judge_atl_sec<- renderPlot({
    
    bail_yrange_2<- 
      bail_df %>% 
      filter(top_arrest_article_section == input$article_section_2)
    bail_yrange_2<- range(bail_yrange_2$first_bail_set_cash, na.rm=TRUE)
    
    judge_median<-
      bail_df %>%
      filter(judge_name == input$judge) %>%
      filter(top_arrest_article_section == input$article_section_2) %>%
      summarise(judge_median = median(first_bail_set_cash, na.rm = TRUE))
    
    bail_df %>%
      filter(judge_name == input$judge) %>%
      filter(top_arrest_article_section == input$article_section_2) %>%
      ggplot(aes(x=first_arraign_date, y=first_bail_set_cash)) +
      geom_boxplot() +
      scale_y_log10(n.breaks=10) +
      geom_hline(yintercept = judge_median$judge_median,
                 color='red', alpha=0.5) +
      annotate('text', x="2020-06-01",
               y=max(bail_yrange_2),
               label=paste0("median bail: ",
                            judge_median$judge_median),
               color="red3") +
      labs(title="Distribution of Bail Amount by Judge and Charge",
           x="Month of Arraignment",
           y="Cash Bail Amount") +
      theme(axis.text.x = element_text(angle = 90, vjust = 0.0, hjust=0))
  }, height = 400, width = 800)
  
}

library(mgcv)
library(ggeffects)
library(ggplot2)
library(patchwork)
library(dplyr)

model_summaries <- data.frame(
  variable = character(),
  term = character(),
  edf = numeric(),
  ref_df = numeric(),
  F = numeric(),
  p_value = numeric(),
  r_squared = numeric(),
  stringsAsFactors = FALSE
)

all_effects <- list()

dependent_vars <- c(
  "n_TUs_norm",
"n_TUs_delta",
"TUs_duration_norm",
"TU_duration_delta",
"n_tokens_norm",
"n_tokens_delta",
"n_lingtoks_norm",
"n_lingtoks_delta",
"n_NVB_norm",
"n_NVB_delta",
"avg_tokens",
"avg_tokens_delta",
"avg_TU_duration",
"avg_TU_duration_delta",
"n_intonationpatterns_norm",
"n_intonationpatterns_delta",
"n_prolongations_norm",
"n_prolongations_delta",
"n_overlaps_norm",
"n_overlaps_delta"
)

df_params <- read.csv("stats/table_params.csv", sep="\t")

df_params$expert <- as.factor(df_params$expert)
df_params$data <- as.factor(df_params$data)
df_params$phase <- as.factor(df_params$phase)
df_params$transcriber <- as.factor(df_params$transcriber)  # your random effect

models <- list()

for (var in dependent_vars) {
  # formula_str <- as.formula(paste0("`", var, "` ~ s(minute, k = 3) + expert + phase + data + s(transcriber, bs = 're')"))
  # cat("\n\n====== GAMM for", var, "======\n")
  formula_str <- as.formula(paste0("`", var, "` ~ s(minute, k = 3) + expert + phase + data + s(transcriber, bs = 're')"))
  cat("\n\n====== GAMM for", var, "======\n")

  model <- gam(formula_str, data = df_params, method = "REML", family = gaussian())
  print(summary(model))
  models[[var]] <- model

smry <- summary(model)

  # Extract smooth and parametric terms separately
  smooth_terms <- smry$s.table
  if (!is.null(smooth_terms)) {
    smooth_df <- data.frame(
      variable = var,
      term = rownames(smooth_terms),
      edf = smooth_terms[, "edf"],
      ref_df = smooth_terms[, "Ref.df"],
      F = smooth_terms[, "F"],
      p_value = smooth_terms[, "p-value"],
      r_squared = rep(smry$r.sq, nrow(smooth_terms))
    )
    model_summaries <- rbind(model_summaries, smooth_df)
  }

  param_terms <- smry$p.table
  if (!is.null(param_terms)) {
    param_df <- data.frame(
      variable = var,
      term = rownames(param_terms),
      edf = NA,
      ref_df = NA,
      F = NA,
      p_value = param_terms[, "Pr(>|t|)"],
      r_squared = rep(smry$r.sq, nrow(param_terms))
    )
    model_summaries <- rbind(model_summaries, param_df)
  }

  predictors <- c("minute", "expert", "phase", "data")

  for (pred in predictors) {
    # Use try() to handle errors (e.g., if a factor has only one level)
    pred_effect <- try(ggpredict(model, terms = pred), silent = TRUE)

    if (!inherits(pred_effect, "try-error")) {
      df <- as.data.frame(pred_effect)
      df$x <- as.character(df$x)  # Ensure x is always character
      df$predictor <- pred
      df$dependent_var <- var
      all_effects[[length(all_effects) + 1]] <- df
    }
  }

  # Plot smooth effect
  png_filename_smooth <- paste0("plots/gam_smooth_", gsub(" ", "_", var), ".png")
  png(png_filename_smooth, width = 800, height = 600)
  plot(model, select = 1, shade = TRUE, main = paste("Smooth effect of minute on", var))
  dev.off()

  # Plot diagnostic checks
  png_filename_diag <- paste0("plots/gam_diag_", gsub(" ", "_", var), ".png")
  png(png_filename_diag, width = 1000, height = 800)
  gam.check(model)
  dev.off()
}

write.csv(model_summaries, "stats/gam_model_summaries.csv", row.names = FALSE)
effects_df <- bind_rows(all_effects)

# Optional: Save to CSV
write.csv(effects_df, "stats/gam_effects_with_ci.csv", row.names = FALSE)


# Ensure the output directory exists
if (!dir.exists("plots")) dir.create("plots")

# Custom theme
effect_theme <- function() {
  theme_minimal(base_size = 14) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5, size = 16),
      axis.title = element_text(size = 14),
      axis.text = element_text(size = 12),
      panel.grid.minor = element_blank(),
      panel.grid.major.y = element_line(color = "gray90"),
      panel.grid.major.x = element_blank(),
      panel.border = element_rect(color = "gray80", fill = NA, size = 0.5),
      plot.margin = margin(10, 15, 10, 15),
      legend.position = "none"
    )
}

# Loop through stored models
for (var in names(models)) {
  model <- models[[var]]
  df <- df_params
  df$fit <- predict(model, se.fit = TRUE)$fit
  df$lower <- df$fit - 1.96 * predict(model, se.fit = TRUE)$se.fit
  df$upper <- df$fit + 1.96 * predict(model, se.fit = TRUE)$se.fit

  # Predicted vs observed plot
  p_pred <- ggplot(df, aes(x = fit, y = .data[[var]], color = data, shape = phase)) +
    geom_errorbar(aes(ymin = lower, ymax = upper), width = 0.05, alpha = 0.5, size = 0.7) +
    geom_point(size = 3, alpha = 0.8) +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "gray40", size = 0.8) +
    labs(
      title = paste("Predicted vs. Observed for", var),
      subtitle = "With 95% Confidence Intervals",
      x = paste("Predicted", var),
      y = paste("Observed", var),
      color = "Data Source",
      shape = "Phase"
    ) +
    scale_color_brewer(palette = "Set1") +
    theme_minimal(base_size = 14) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      plot.subtitle = element_text(hjust = 0.5, color = "gray50"),
      legend.position = "bottom",
      panel.grid.minor = element_blank(),
      panel.border = element_rect(color = "gray80", fill = NA, size = 0.5),
      plot.margin = margin(15, 15, 15, 15)
    ) +
    guides(
      color = guide_legend(override.aes = list(size = 3)),
      shape = guide_legend(override.aes = list(size = 3))
    )

  ggsave(paste0("plots/predicted_vs_observed_", gsub(" ", "_", var), ".png"),
         p_pred, width = 7, height = 6, dpi = 300)

  # Marginal effects
  eff_expert <- ggpredict(model, terms = "expert")
  eff_data <- ggpredict(model, terms = "data")
  eff_phase <- ggpredict(model, terms = "phase")

  # Expert p-value
  p_val <- summary(model)$p.table["expertnovice", "Pr(>|t|)"]
  p_label <- paste0("p = ", format.pval(p_val, digits = 3, eps = .001))

  # Plots
  p_expert <- ggplot(eff_expert, aes(x = x, y = predicted)) +
    geom_point(size = 4, color = "#0072B2", fill = "white", shape = 21, stroke = 1.5) +
    geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.1, color = "#0072B2", linewidth = 1) +
    labs(title = "Effect of Expertise", x = "Expertise", y = paste("Predicted", var)) +
    effect_theme()

  p_data <- ggplot(eff_data, aes(x = x, y = predicted)) +
    geom_point(size = 4, color = "#E69F00", fill = "white", shape = 22, stroke = 1.5) +
    geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.1, color = "#E69F00", linewidth = 1) +
    labs(title = "Effect of Data Type", x = "Data", y = paste("Predicted", var)) +
    effect_theme()

  p_phase <- ggplot(eff_phase, aes(x = x, y = predicted)) +
    geom_point(size = 4, color = "#009E73", fill = "white", shape = 24, stroke = 1.5) +
    geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.1, color = "#009E73", linewidth = 1) +
    labs(title = "Effect of Phase", x = "Phase", y = paste("Predicted", var)) +
    effect_theme()

  combined <- (p_expert | p_data | p_phase) +
    plot_annotation(title = paste("Marginal Effects on", var),
                    theme = theme(plot.title = element_text(face = "bold", size = 18, hjust = 0.5)))

  ggsave(paste0("plots/marginal_effects_", gsub(" ", "_", var), ".png"),
         combined, width = 14, height = 5, dpi = 300, bg = "white")
}
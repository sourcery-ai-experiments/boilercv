nbqa black data/docs
nbqa ruff --fix-only data/docs
nb-clean clean --remove-empty-cells --preserve-cell-outputs --preserve-cell-metadata tags special -- data/docs

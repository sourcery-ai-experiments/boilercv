<#.SYNOPSIS
Generate a document from a notebook.
#>

Param(
    # Notebook to generate a document from.
    [Parameter(Mandatory, ValueFromPipeline)]$Notebook
)
begin {
    $RootDir = Push-Location -PassThru "$PSSCriptRoot/../.."
    $DataDir = "$RootDir/data"
    $MdDir = "$DataDir/md"

    $DocxDir = "$DataDir/docx"
    if (Test-Path $DocxDir) {Remove-Item $DocxDir -Recurse}
    New-Item $DocxDir -ItemType Directory
    $ToMarkdown = @(
        '--to', 'markdown'
        '--no-input' # Remove notebook input cells
        '--output-dir', $MdDir # Write to a separate output folder
    )

    $DocxWithCitations = @(
        '--standalone' # Don't produce a document fragment.
        '--from', 'markdown-auto_identifiers' # Avoids bookmark pollution around Markdown headers
        '--reference-doc', 'G:/My Drive/Blake/School/Grad/Documents/Templates/Office Templates/AMSL Monthly.dotx' # The template to export literature reviews to
        # Lua filter and metadata passed to it
        '--lua-filter', "$PSSCriptRoot/zotero.lua" # Needs to be the one downloaded from the tutorial page https://retorque.re/zotero-better-bibtex/exporting/pandoc/#from-markdown-to-zotero-live-citations
        '--metadata', "zotero_csl_style:$PSSCriptRoot/international-journal-of-heat-and-mass-transfer.csl" # Must also be installed in Zotero
        '--metadata', 'zotero_library:3' # Corresponds to "Nucleate pool boiling [3]"
    )

    $HtmlDir = "$DataDir/html"
    if (Test-Path $HtmlDir) {Remove-Item $HtmlDir -Recurse}
    New-Item $HtmlDir -ItemType Directory
    $ToHtml = @(
        '--to', 'html'
        '--no-input' # Remove notebook input cells
        '--output-dir', $HtmlDir # Write to a separate output folder
    )
}
process {
    $Notebook = Get-Item $Notebook
    jupyter nbconvert @ToMarkdown $Notebook
    jupyter nbconvert @ToHtml $Notebook
    Push-Location $MdDir
    $Name = $Notebook.BaseName
    Get-Item "$Name.md" | Get-Content |
        pandoc @DocxWithCitations --output "$DocxDir/$Name.docx"
    Pop-Location
}

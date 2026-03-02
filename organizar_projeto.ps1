Write-Host "[*] INICIANDO ORGANIZAÇÃO DO PROJETO..." -ForegroundColor Cyan

# Criação das pastas caso não existam
$pastas = @(
    "notebooks", "data\processed", "data\raw", "models", 
    "reports\figures", "src\miner", "src\utils", "docker"
)

foreach ($pasta in $pastas) {
    if (-not (Test-Path $pasta)) {
        New-Item -ItemType Directory -Path $pasta | Out-Null
        Write-Host "[+] Diretório criado: $pasta" -ForegroundColor Green
    }
}

# Definição das regras de destino
$Regras = @{
    ".ipynb"   = "notebooks\"
    ".parquet" = "data\processed\"
    ".csv"     = "data\processed\"
    ".json"    = "models\"
    ".joblib"  = "models\"
    ".pkl"     = "models\"
    ".png"     = "reports\figures\"
    ".arff"    = "data\raw\"
    ".txt"     = "data\raw\"
    ".jpg"     = "data\raw\"
}

$Arquivos = Get-ChildItem -Path "." -Recurse -File | Where-Object { $_.FullName -notlike "*\.git*" -and $_.FullName -notlike "*\Git\*" }

foreach ($Arq in $Arquivos) {
    $Destino = ""
    $Mover = $false

    # Regra baseada em extensão
    if ($Regras.ContainsKey($Arq.Extension)) {
        $Destino = $Regras[$Arq.Extension]
        $Mover = $true
    }

    # Regras especiais para Scripts
    if ($Arq.Extension -eq ".py" -or $Arq.Extension -eq ".ps1") {
        # O proprio script nao deve ser movido
        if ($Arq.Name -eq "organizar_projeto.ps1") {
            $Mover = $false
        }
        elseif ($Arq.Name -match "baixar|miner|shodan|analysis") { $Destino = "src\miner\"; $Mover = $true }
        elseif ($Arq.Name -match "fix|refactor|edit|organizar|check|simulator|tmp_read_nb|extract_nb") { $Destino = "src\utils\"; $Mover = $true }
    }

    # Regras para Docker e Utilitários Gerais
    if ($Arq.Name -match "Dockerfile|docker-compose|\.dockerignore") { $Destino = "docker\"; $Mover = $true }
    if ($Arq.Name -match "out_.*\.txt") { $Destino = "src\utils\"; $Mover = $true }

    # Arquivos que DEVEM ficar na raiz
    if ($Arq.Name -match "README|gitignore|requirements|app\.py|\.env") { $Destino = ""; $Mover = $false }

    if ($Mover -and $Destino -ne "") {
        # Validar se o arquivo não está já no destino correto para evitar erros
        $caminhoDestinoCompleto = Resolve-Path $Destino -ErrorAction SilentlyContinue
        if ($caminhoDestinoCompleto -and ($Arq.DirectoryName -eq $caminhoDestinoCompleto.Path)) {
            continue
        }
        
        try {
            Move-Item -Path $Arq.FullName -Destination $Destino -Force
            Write-Host " -> Movido: $($Arq.Name) para $Destino" -ForegroundColor Yellow
        }
        catch {
            Write-Host " [!] Erro ao mover $($Arq.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n[*] Removendo pastas vazias..." -ForegroundColor Magenta
# Remove pastas vazias de forma recursiva (menos o .git)
$pastasVazias = Get-ChildItem -Path "." -Recurse -Directory | Where-Object { $_.FullName -notlike "*\.git*" -and (Get-ChildItem -Path $_.FullName -Force).Count -eq 0 }
foreach ($pasta in $pastasVazias) {
    Remove-Item -Path $pasta.FullName -Force
    Write-Host " [-] Pasta removida: $($pasta.FullName)" -ForegroundColor DarkGray
}

Write-Host "`n[*] Organização concluída com sucesso!" -ForegroundColor Cyan

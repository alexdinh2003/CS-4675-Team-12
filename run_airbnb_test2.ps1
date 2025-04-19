# Stop on any error
$ErrorActionPreference = 'Stop'

# Move into the directory where this .ps1 lives
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# Node ports (ensure these match your Node_DHT.py configuration)
$port1 = 9000
$port2 = 9200
$port3 = 9300
$logDir = "logs"

# Create logs directory if it doesn't exist
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

Write-Host "=== Starting nodes ==="

# Start each Python node (bootstrap port1 first)
$p1 = Start-Process python `
    -WorkingDirectory $scriptDir `
    -ArgumentList "-u", "Node_DHT.py", $port1 `
    -RedirectStandardOutput "$logDir\node1.out.log" `
    -RedirectStandardError  "$logDir\node1.err.log" `
    -PassThru
Start-Sleep -Seconds 1

$p2 = Start-Process python `
    -WorkingDirectory $scriptDir `
    -ArgumentList "-u", "Node_DHT.py", $port2, $port1 `
    -RedirectStandardOutput "$logDir\node2.out.log" `
    -RedirectStandardError  "$logDir\node2.err.log" `
    -PassThru
Start-Sleep -Seconds 1

$p3 = Start-Process python `
    -WorkingDirectory $scriptDir `
    -ArgumentList "-u", "Node_DHT.py", $port3, $port1 `
    -RedirectStandardOutput "$logDir\node3.out.log" `
    -RedirectStandardError  "$logDir\node3.err.log" `
    -PassThru

# Wait until each port is accepting connections
$ports = @($port1, $port2, $port3)
foreach ($port in $ports) {
    Write-Host "Waiting for node on port $port to come online..."
    while (-not (Test-NetConnection -ComputerName 'localhost' -Port $port).TcpTestSucceeded) {
        Start-Sleep -Milliseconds 200
    }
    Write-Host "→ Port $port is now accepting connections."
}

# Helper function to send TCP messages
function Send-Message {
    param(
        [string]$Message,
        [int]$Port
    )
    $client = [System.Net.Sockets.TcpClient]::new('localhost', $Port)
    $stream = $client.GetStream()
    $writer = [System.IO.StreamWriter]::new($stream)
    $writer.WriteLine($Message)
    $writer.Flush()
    Start-Sleep -Milliseconds 200
    $reader = [System.IO.StreamReader]::new($stream)
    $response = $reader.ReadToEnd()
    $client.Close()
    return $response
}

# ========== DEFINE 10 LISTINGS ==========
$listings = @(
    '{"id":"l1","title":"Cozy Seattle Room","host_id":"u1","host_name":"Alice","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Private room","price":85,"minimum_nights":2,"number_of_reviews":12,"last_review":"2023-01-01","reviews_per_month":0.3,"calculated_host_listings_count":1,"availability_365":200,"zipcode":98101}',
    '{"id":"l2","title":"Manhattan Apartment","host_id":"u2","host_name":"Bob","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Entire home","price":200,"minimum_nights":3,"number_of_reviews":28,"last_review":"2023-03-15","reviews_per_month":0.7,"calculated_host_listings_count":2,"availability_365":150,"zipcode":10001}',
    '{"id":"l3","title":"Charming SF Studio","host_id":"u3","host_name":"Carol","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Entire home","price":175,"minimum_nights":1,"number_of_reviews":40,"last_review":"2023-02-12","reviews_per_month":1.2,"calculated_host_listings_count":3,"availability_365":300,"zipcode":94121}',
    '{"id":"l4","title":"Seattle Downtown Condo","host_id":"u4","host_name":"Dana","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Entire home","price":150,"minimum_nights":2,"number_of_reviews":10,"last_review":"2023-03-10","reviews_per_month":0.5,"calculated_host_listings_count":1,"availability_365":180,"zipcode":98101}',
    '{"id":"l5","title":"NYC Loft","host_id":"u5","host_name":"Evan","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Loft","price":120,"minimum_nights":2,"number_of_reviews":18,"last_review":"2023-01-20","reviews_per_month":0.6,"calculated_host_listings_count":2,"availability_365":220,"zipcode":10001}',
    '{"id":"l6","title":"SF Modern Flat","host_id":"u6","host_name":"Fiona","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Apartment","price":130,"minimum_nights":2,"number_of_reviews":25,"last_review":"2023-04-01","reviews_per_month":0.8,"calculated_host_listings_count":4,"availability_365":160,"zipcode":94121}',
    '{"id":"l7","title":"Seattle Loft","host_id":"u7","host_name":"George","location":"Seattle","latitude":47.6,"longitude":-122.3,"room_type":"Loft","price":140,"minimum_nights":3,"number_of_reviews":22,"last_review":"2023-02-28","reviews_per_month":0.9,"calculated_host_listings_count":3,"availability_365":210,"zipcode":98101}',
    '{"id":"l8","title":"NYC Studio","host_id":"u8","host_name":"Hannah","location":"New York","latitude":40.7,"longitude":-73.9,"room_type":"Studio","price":90,"minimum_nights":1,"number_of_reviews":12,"last_review":"2023-03-05","reviews_per_month":0.4,"calculated_host_listings_count":1,"availability_365":190,"zipcode":10001}',
    '{"id":"l9","title":"SF Downtown Cabin","host_id":"u9","host_name":"Ian","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Cabin","price":110,"minimum_nights":2,"number_of_reviews":15,"last_review":"2023-01-15","reviews_per_month":0.5,"calculated_host_listings_count":2,"availability_365":170,"zipcode":94121}',
    '{"id":"l10","title":"SF Cozy Cottage","host_id":"u10","host_name":"Jack","location":"San Francisco","latitude":37.7,"longitude":-122.4,"room_type":"Cottage","price":95,"minimum_nights":1,"number_of_reviews":7,"last_review":"2023-04-01","reviews_per_month":0.2,"calculated_host_listings_count":1,"availability_365":150,"zipcode":94121}'
)

Write-Host "=== Adding 10 listings using a loop ==="
$ports = @($port1, $port2, $port3)
for ($i = 0; $i -lt $listings.Count; $i++) {
    $listing = $listings[$i]
    $port    = $ports[$i % $ports.Count]
    $listingId = ($listing | ConvertFrom-Json).id

    Write-Host "Adding listing $listingId on port $port"
    Send-Message "add_listing|$listing" $port | Out-Null

    Write-Host "Querying added listing by ID"
    $response = Send-Message "get_listing_by_id|$listingId" $port
    Write-Host "Resp: $response"
}

# ========== QUERY BY CITY ==========
Write-Host "`n=== Individual city queries ==="
$cities = @("Seattle","New York","San Francisco")
foreach ($city in $cities) {
    Write-Host "`nQuery for city: $city"
    $response = Send-Message "get_listings_by_city|$city" $port1
    Write-Host "Response: $response"
}

# ========== QUERY BY ZIPCODE ==========
Write-Host "`n=== Individual zipcode queries ==="
$zips = @(98101,10001,94121)
foreach ($zip in $zips) {
    Write-Host "`nQuery for zipcode: $zip"
    $response = Send-Message "get_listings_by_zip|$zip" $port2
    Write-Host "Response: $response"
}

# ========== TEARDOWN ==========
Write-Host "`n=== Tearing down nodes ==="
$p1, $p2, $p3 | ForEach-Object { Stop-Process -Id $_.Id -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1
Write-Host "✅ Test complete. Logs available in $logDir/"

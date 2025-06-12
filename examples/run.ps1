param(
    [string]$Path="examples/example.py",
    [string]$Destination = "examples/example_res.py",
    [switch]$PrintAfter,
    [switch]$RunAfter,
    [switch]$Benchmark,
    $BenchmarkRepeats="auto"
)

$pythonExecutable = "py"


& $pythonExecutable one.py $Path -o $Destination

if ($PrintAfter)
{
    Write-Host "Resulting file:" -ForegroundColor Green
    Get-Content $Destination -Raw | Out-Host
}

if ($RunAfter)
{
    Write-Host "Run result:" -ForegroundColor Green
    & $pythonExecutable $Destination
}

if ($Benchmark)
{
    function Bench
    {
        param(
            [string]$file,
            $repeats
        )


        if ($repeats -eq "auto")
        {
            $WarmupTime = 0.5
            $TestingTime = 4.0

            $time = [System.Collections.Generic.List[double]]::new();

            $start = [datetime]::UtcNow
            do
            {
                $nowTime = ([datetime]::UtcNow - $start).TotalSeconds
                Write-Progress -Activity "benchmark $file" -Status "warmup" -PercentComplete ([int]([math]::min(100, $nowTime / $WarmupTime * 100)))
            }
            while ($nowTime -lt $WarmupTime)


            $start = [datetime]::UtcNow
            do
            {
                [void]$time.Add((Measure-Command { & $pythonExecutable $Destination }).TotalMilliseconds)
                $nowTime = ([datetime]::UtcNow - $start).TotalSeconds
                Write-Progress -Activity "benchmark $file" -Status "running" -PercentComplete ([int]([math]::min(100, $nowTime / $TestingTime * 100)))
            }
            while ($nowTime -lt $TestingTime)


            Write-Progress -Activity "benchmark $file" -Status "running" -Completed
        }
        else
        {
            $time = [System.Collections.Generic.List[double]]::new();
            for ($i = 0; $i -lt $repeats; ++$i)
            {
                [void]$time.Add((Measure-Command { & $pythonExecutable $Destination }).TotalMilliseconds)
                Write-Progress -Activity "benchmark $file" -Status "running" -PercentComplete ([int]([math]::min(100, ($i + 1) / $repeats * 100)))
            }
            Write-Progress -Activity "benchmark $file" -Status "running" -Completed
        }

        return @($time)
    }

    Write-Host "Benchmarking..." -ForegroundColor Green

    $was = Bench $Path        -repeats $BenchmarkRepeats
    $now = Bench $Destination -repeats $BenchmarkRepeats

    Write-Host "Benchmark results: " -ForegroundColor Green

    Write-Host "source: " -ForegroundColor Green
    ($a = ($was | Measure-Object -AllStats)) | Select-Object Count, Average, Maximum, Minimum, StandardDeviation | Out-Host
    Write-Host "result: " -ForegroundColor Green
    ($b = ($now | Measure-Object -AllStats)) | Select-Object Count, Average, Maximum, Minimum, StandardDeviation | Out-Host


    if ($a.Average -gt 1e-12)
    {
        $speed = $b.Average / $a.Average * 100
    }
    else
    {
        $speed = "inf"
    }
    Write-Host "At average, new solution is $([math]::round($speed, 1))% of previous." -ForegroundColor Yellow

    if ([math]::abs($speed - 100) -lt 2.0)
    {
        Write-Host "Them are almost equal!" -ForegroundColor Yellow
    }
    elseif ($speed -lt 100)
    {
        $tt = 100 / $speed;
        Write-Host "new is $tt times faster!" -ForegroundColor Green
    }
    else
    {
        $tt = $speed / 100;
        Write-Host "old is $tt times slower!" -ForegroundColor Red
    }

}
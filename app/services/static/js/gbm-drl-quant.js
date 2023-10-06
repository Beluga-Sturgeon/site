const fs = require('fs');
const { exec } = require('child_process');
const path = require('path');
const readline = require('readline');
const { promisify } = require('util');

const readFile = promisify(fs.readFile);
const execPromise = promisify(exec);

async function readStats() {
    const filePath = path.join('app', 'services', 'gbm-drl-quant', 'res', 'stats.txt');
    
    try {
        const data = await readFile(filePath, 'utf8');
        const lines = data.split('\n');
        const firstLineData = lines[0].split(',');
        
        const df = {
            Ticker: firstLineData[0],
            "Annualized Return benchmark": firstLineData[1],
            "Stdev of Returns benchmark": firstLineData[2],
            "Shape Ratio benchmark": firstLineData[3],
            "Maximum Drawdown benchmark": firstLineData[4],
            "Annualized Return model": firstLineData[5],
            "Stdev of Returns model": firstLineData[6],
            "Shape Ratio model": firstLineData[7],
            "Maximum Drawdown model": firstLineData[8]
        };
        
        return df;
    } catch (error) {
        console.error(error);
        return null;
    }
}

async function readLog() {
    const logFilePath = path.join('app', 'services', 'gbm-drl-quant', 'res', 'log.txt');
    
    try {
        const data = await readFile(logFilePath, 'utf8');
        const lines = data.split('\n');
        const lastLine = lines[lines.length - 1];
        const columns = ["X", "SPY", "IEF", "GSG", "EUR=X", "action", "benchmark", "model"];
        const lastLineData = lastLine.split(',');
        
        const df = {};
        columns.forEach((column, index) => {
            df[column] = lastLineData[index];
        });
        
        return df;
    } catch (error) {
        console.error(error);
        return null;
    }
}

async function runTest(ticker) {
    const directoryPath = path.join('app', 'services', 'gbm-drl-quant');
    const command = `.\\exec test ${ticker} .\\models\\checkpoint`;
    
    try {
        await execPromise(`cd ${directoryPath} && ${command}`);
    } catch (error) {
        console.error(`Error: ${error}`);
    }
}

async function getData(ticker) {
    await runTest(ticker);
    
    const log = await readLog();
    const stats = await readStats();
    
    return {
        ticker,
        action: log.action,
        e_a_r: stats["Annualized Return model"],
        std: stats["Stdev of Returns model"],
        sharperatio: stats["Shape Ratio model"],
        maxdrawdown: stats["Maximum Drawdown model"]
    };
}




async function updateActionBox() {
    ticker = document.URL.split("/").pop();

    data = await getData(ticker);

    // Find the elements by their class names
    const recommendedActionElement = document.querySelector('.recommendedaction .action');
    const annualizedReturnElement = document.querySelector('.annualizedreturn .numbervalue');
    const stdReturnElement = document.querySelector('.stdreturn .numbervalue');
    const sharpeRatioElement = document.querySelector('.sharperatio .numbervalue');
    const maxDrawdownElement = document.querySelector('.maxdrawdown .numbervalue');

    // Update the elements with the data
    recommendedActionElement.textContent = data.action;
    annualizedReturnElement.textContent = data.e_a_r;
    stdReturnElement.textContent = data.std;
    sharpeRatioElement.textContent = data.sharperatio;
    maxDrawdownElement.textContent = data.maxdrawdown;

}

// Call the updateActionBox function when your page is ready
document.addEventListener("DOMContentLoaded", async () => {
    await updateActionBox();
  });
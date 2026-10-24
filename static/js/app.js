/**
 * Boolean Expression Compiler - Interactive Workbench Controller
 * Handles editor line numbers, symbol table management, REST API communication,
 * SVG AST tree visualization, and tabbed inspection views.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const expressionInput = document.getElementById('expressionInput');
    const lineNumbers = document.getElementById('lineNumbers');
    const btnCompile = document.getElementById('btnCompile');
    const btnClear = document.getElementById('btnClear');
    const exampleSelector = document.getElementById('exampleSelector');
    const btnAddSymbol = document.getElementById('btnAddSymbol');
    const symbolTableBody = document.getElementById('symbolTableBody');
    const chkStrictMode = document.getElementById('chkStrictMode');
    const chkEvaluate = document.getElementById('chkEvaluate');
    const backendStatus = document.getElementById('backendStatus');
    const statusText = document.getElementById('statusText');
    const toastContainer = document.getElementById('toastContainer');

    // Overview Tab Elements
    const masterStatusCard = document.getElementById('masterStatusCard');
    const statusLead = document.getElementById('statusLead');
    const statusSub = document.getElementById('statusSub');
    const statusIcon = document.getElementById('statusIcon');
    const metricResult = document.getElementById('metricResult');
    const metricType = document.getElementById('metricType');
    const metricEval = document.getElementById('metricEval');
    const metricTime = document.getElementById('metricTime');
    const pipelineStepper = document.getElementById('pipelineStepper');
    const evalDetailsBox = document.getElementById('evalDetailsBox');

    // Tab & Badges
    const resultsTabs = document.getElementById('resultsTabs');
    const badgeTokenCount = document.getElementById('badgeTokenCount');
    const badgeErrorCount = document.getElementById('badgeErrorCount');

    // Tokens Elements
    const tokensTableBody = document.getElementById('tokensTableBody');
    const btnCopyTokens = document.getElementById('btnCopyTokens');

    // AST Elements
    const astSvgContainer = document.getElementById('astSvgContainer');
    const astTextContainer = document.getElementById('astTextContainer');
    const astTreeText = document.getElementById('astTreeText');
    const btnViewSvg = document.getElementById('btnViewSvg');
    const btnViewText = document.getElementById('btnViewText');
    const btnCopyAst = document.getElementById('btnCopyAst');

    // Grammar & Semantics Elements
    const grammarDerivationBox = document.getElementById('grammarDerivationBox');
    const usedVariablesTableBody = document.getElementById('usedVariablesTableBody');
    const errorsContainer = document.getElementById('errorsContainer');

    // Modal
    const btnHelp = document.getElementById('btnHelp');
    const btnCloseHelp = document.getElementById('btnCloseHelp');
    const modalHelp = document.getElementById('modalHelp');

    // State Variables
    let lastCompilationResult = null;

    // Initial Symbol Table Presets
    const initialSymbols = [
        { name: 'a', type: 'number', value: '15' },
        { name: 'b', type: 'number', value: '10' },
        { name: 'c', type: 'number', value: '20' },
        { name: 'd', type: 'number', value: '30' },
        { name: 'x1', type: 'number', value: '50' },
        { name: 'isValid', type: 'boolean', value: 'true' }
    ];

    // ==========================================
    // 1. Initialization & Backend Health Check
    // ==========================================
    function checkBackendHealth() {
        const startTime = performance.now();
        fetch('/api/health')
            .then(res => res.json())
            .then(data => {
                const latency = Math.round(performance.now() - startTime);
                backendStatus.className = 'status-indicator online';
                statusText.textContent = `Backend Online (${latency}ms) • Python ${data.python_version || '3.12'}`;
            })
            .catch(() => {
                backendStatus.className = 'status-indicator offline';
                statusText.textContent = 'Backend Offline';
                showToast('Unable to reach compiler backend. Please ensure Flask app is running.', 'error');
            });
    }

    // ==========================================
    // 2. Line Number & Editor Synchronization
    // ==========================================
    function updateLineNumbers() {
        const lines = expressionInput.value.split('\n').length;
        let lineNumsHtml = '';
        for (let i = 1; i <= Math.max(lines, 1); i++) {
            lineNumsHtml += `${i}<br>`;
        }
        lineNumbers.innerHTML = lineNumsHtml;
    }

    expressionInput.addEventListener('input', updateLineNumbers);
    expressionInput.addEventListener('scroll', () => {
        lineNumbers.scrollTop = expressionInput.scrollTop;
    });

    // Keyboard shortcut: Ctrl + Enter / Cmd + Enter
    expressionInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            runCompilation();
        }
    });

    // ==========================================
    // 3. Symbol Table Management
    // ==========================================
    function renderSymbolRow(name = '', type = 'number', value = '') {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <input type="text" class="sym-input sym-name" value="${escapeHtml(name)}" placeholder="e.g. x1" />
            </td>
            <td>
                <select class="sym-select sym-type">
                    <option value="number" ${type === 'number' ? 'selected' : ''}>number</option>
                    <option value="boolean" ${type === 'boolean' ? 'selected' : ''}>boolean</option>
                </select>
            </td>
            <td>
                <input type="text" class="sym-input sym-value" value="${escapeHtml(String(value))}" placeholder="${type === 'boolean' ? 'true / false' : 'e.g. 10'}" />
            </td>
            <td style="text-align: center;">
                <button type="button" class="btn-remove-sym" title="Remove variable">&times;</button>
            </td>
        `;

        const typeSelect = row.querySelector('.sym-type');
        const valInput = row.querySelector('.sym-value');
        typeSelect.addEventListener('change', () => {
            valInput.placeholder = typeSelect.value === 'boolean' ? 'true / false' : 'e.g. 10';
        });

        row.querySelector('.btn-remove-sym').addEventListener('click', () => {
            row.remove();
        });

        symbolTableBody.appendChild(row);
    }

    function initSymbolTable() {
        symbolTableBody.innerHTML = '';
        initialSymbols.forEach(s => renderSymbolRow(s.name, s.type, s.value));
    }

    btnAddSymbol.addEventListener('click', () => {
        renderSymbolRow('', 'number', '');
    });

    function getSymbolsFromUI() {
        const symbols = [];
        const rows = symbolTableBody.querySelectorAll('tr');
        rows.forEach(r => {
            const name = r.querySelector('.sym-name')?.value.trim();
            const type = r.querySelector('.sym-type')?.value;
            const val = r.querySelector('.sym-value')?.value.trim();
            if (name) {
                symbols.push({ name, type, value: val });
            }
        });
        return symbols;
    }

    // ==========================================
    // 4. Tab Navigation
    // ==========================================
    resultsTabs.addEventListener('click', (e) => {
        const tabBtn = e.target.closest('.tab-btn');
        if (!tabBtn) return;

        const targetTabId = tabBtn.getAttribute('data-tab');
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        tabBtn.classList.add('active');
        tabBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        const targetPane = document.getElementById(targetTabId);
        if (targetPane) targetPane.classList.add('active');
    });

    function switchTab(tabId) {
        const btn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
        if (btn) btn.click();
    }

    // ==========================================
    // 5. Example Selector & Clear
    // ==========================================
    exampleSelector.addEventListener('change', () => {
        const expr = exampleSelector.value;
        if (expr) {
            expressionInput.value = expr;
            updateLineNumbers();
            showToast(`Loaded example: ${expr}`, 'info');
        }
    });

    btnClear.addEventListener('click', () => {
        expressionInput.value = '';
        updateLineNumbers();
        expressionInput.focus();
        showToast('Editor cleared', 'info');
    });

    // ==========================================
    // 6. Compilation Execution Pipeline
    // ==========================================
    async function runCompilation() {
        const expression = expressionInput.value;
        const symbols = getSymbolsFromUI();
        const options = {
            strict_mode: chkStrictMode.checked,
            evaluate: chkEvaluate.checked
        };

        btnCompile.classList.add('loading');
        btnCompile.disabled = true;

        try {
            const response = await fetch('/api/compile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expression, symbols, options })
            });

            const result = await response.json();
            lastCompilationResult = result;
            renderCompilationResults(result);

            if (result.success) {
                showToast('Compilation completed successfully!', 'success');
            } else {
                showToast('Compilation found errors. See Errors tab for details.', 'error');
            }
        } catch (error) {
            console.error('Compilation fetch failed:', error);
            showToast(`Failed to connect to backend: ${error.message}`, 'error');
        } finally {
            btnCompile.classList.remove('loading');
            btnCompile.disabled = false;
        }
    }

    btnCompile.addEventListener('click', runCompilation);

    // ==========================================
    // 7. Results Rendering
    // ==========================================
    function renderCompilationResults(res) {
        // 1. Status Overview Header
        const totalDuration = res.phases ? res.phases.reduce((acc, p) => acc + (p.duration_ms || 0), 0) : 0;
        metricTime.textContent = `${totalDuration.toFixed(2)} ms`;

        if (res.success) {
            masterStatusCard.className = 'status-card success-border';
            statusLead.textContent = 'Compilation Succeeded';
            statusSub.textContent = 'All phases passed: Lexical, Syntactic, and Semantic type verification completed without errors.';
            statusIcon.textContent = '✓';
            statusIcon.style.color = 'var(--color-success)';
            metricResult.textContent = 'SUCCESS';
            metricResult.style.color = 'var(--color-success)';
        } else {
            masterStatusCard.className = 'status-card error-border';
            statusLead.textContent = 'Compilation Failed';
            statusSub.textContent = `Pipeline aborted with ${res.errors.length} error(s). Review error diagnostic output.`;
            statusIcon.textContent = '✕';
            statusIcon.style.color = 'var(--color-danger)';
            metricResult.textContent = 'FAILED';
            metricResult.style.color = 'var(--color-danger)';
        }

        // Inferred Type & Evaluation Badges
        metricType.textContent = res.inferred_type ? res.inferred_type.toUpperCase() : 'NONE';
        if (res.evaluation && res.evaluation.computed) {
            const isTrue = res.evaluation.result === true;
            metricEval.textContent = isTrue ? 'TRUE' : 'FALSE';
            metricEval.style.color = isTrue ? '#34D399' : '#F87171';
        } else {
            metricEval.textContent = 'N/A';
            metricEval.style.color = 'var(--text-muted)';
        }

        // Stepper
        renderPipelineStepper(res.phases || []);

        // Evaluation Box
        renderEvaluationDetails(res.evaluation);

        // 2. Tokens Tab
        renderTokens(res.tokens || []);
        badgeTokenCount.textContent = res.tokens ? res.tokens.length : 0;

        // 3. AST Tab
        renderAst(res.ast, res.ast_tree_str);

        // 4. Grammar & Derivation Tab
        renderGrammarDerivation(res);

        // 5. Semantics Tab
        renderSemantics(res);

        // 6. Errors Tab
        renderErrors(res.errors || [], res.warnings || []);
        badgeErrorCount.textContent = (res.errors ? res.errors.length : 0);

        // Auto-switch tab if failed
        if (!res.success && res.errors && res.errors.length > 0) {
            // Keep on overview or switch to errors
        }
    }

    // Pipeline Stepper
    function renderPipelineStepper(phases) {
        if (!phases || phases.length === 0) {
            pipelineStepper.innerHTML = '<div class="empty-state">No phases recorded.</div>';
            return;
        }

        let html = '';
        phases.forEach(p => {
            const badgeClass = p.status === 'success' ? 'badge-success' : (p.status === 'failed' ? 'badge-failed' : 'badge-skipped');
            const itemClass = p.status === 'success' ? 'phase-success' : (p.status === 'failed' ? 'phase-failed' : 'phase-skipped');
            html += `
                <div class="phase-item ${itemClass}">
                    <div class="phase-info">
                        <span class="phase-name">${escapeHtml(p.name)}</span>
                        <span class="phase-details">${escapeHtml(p.details || '')}</span>
                    </div>
                    <div class="phase-meta">
                        <span class="phase-badge ${badgeClass}">${escapeHtml(p.status)}</span>
                        <span style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">${p.duration_ms}ms</span>
                    </div>
                </div>
            `;
        });
        pipelineStepper.innerHTML = html;
    }

    // Evaluation Details
    function renderEvaluationDetails(evaluation) {
        if (!evaluation) {
            evalDetailsBox.innerHTML = '<p class="text-muted">Evaluation feature disabled in compiler options.</p>';
            return;
        }

        if (evaluation.computed) {
            evalDetailsBox.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <span style="font-weight: 600; color: #F1F5F9;">Evaluation Result: </span>
                        <span class="badge ${evaluation.result ? 'phase-badge badge-success' : 'phase-badge badge-failed'}" style="font-size: 0.85rem; padding: 0.2rem 0.6rem;">
                            ${evaluation.result_str}
                        </span>
                    </div>
                    <span style="font-size: 0.78rem; color: #10B981;">${escapeHtml(evaluation.status)}</span>
                </div>
                <p style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--text-secondary);">${escapeHtml(evaluation.message)}</p>
            `;
        } else {
            evalDetailsBox.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-weight: 600; color: #FBBF24;">${escapeHtml(evaluation.status)}</span>
                </div>
                <p style="margin-top: 0.4rem; font-size: 0.8rem; color: var(--text-secondary);">${escapeHtml(evaluation.message)}</p>
            `;
        }
    }

    // Tokens Table
    function renderTokens(tokens) {
        if (!tokens || tokens.length === 0) {
            tokensTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No tokens generated.</td></tr>';
            return;
        }

        let html = '';
        tokens.forEach((t, idx) => {
            let badgeClass = 'token-OP';
            if (t.type === 'IDENTIFIER') badgeClass = 'token-IDENTIFIER';
            else if (t.type === 'NUMBER') badgeClass = 'token-NUMBER';
            else if (t.type === 'BOOLEAN') badgeClass = 'token-BOOLEAN';
            else if (t.type === 'LPAREN' || t.type === 'RPAREN' || t.type === 'EOF') badgeClass = 'token-DELIM';

            const valStr = t.value !== null && t.value !== undefined ? String(t.value) : '-';

            html += `
                <tr>
                    <td style="color: var(--text-muted); font-family: var(--font-mono);">${idx + 1}</td>
                    <td><span class="token-badge ${badgeClass}">${escapeHtml(t.type)}</span></td>
                    <td><code style="color: #F8FAFC; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">${escapeHtml(t.lexeme)}</code></td>
                    <td style="font-family: var(--font-mono);">${t.line}</td>
                    <td style="font-family: var(--font-mono);">${t.column}</td>
                    <td style="font-family: var(--font-mono); color: #38BDF8;">${escapeHtml(valStr)}</td>
                </tr>
            `;
        });
        tokensTableBody.innerHTML = html;
    }

    // AST Rendering (Visual SVG + Text)
    function renderAst(ast, treeStr) {
        astTreeText.textContent = treeStr || 'No AST available';

        if (!ast) {
            astSvgContainer.innerHTML = '<div class="empty-state">No AST available for this expression.</div>';
            return;
        }

        // Generate SVG visualization of AST
        try {
            const svgContent = generateAstSvg(ast);
            astSvgContainer.innerHTML = svgContent;
        } catch (e) {
            console.error('Failed to render SVG AST:', e);
            astSvgContainer.innerHTML = `<div class="empty-state">Visual tree layout failed: ${escapeHtml(e.message)}. Please check Indented Tree View.</div>`;
        }
    }

    // Dynamic SVG AST Tree Generator
    function generateAstSvg(root) {
        // Assign coordinates using a tree layout algorithm
        let idCounter = 0;
        function prepareNode(node, depth = 0) {
            node._id = ++idCounter;
            node._depth = depth;
            node._children = [];

            if (node.node_type === 'BinaryOpNode') {
                if (node.left) node._children.push(prepareNode(node.left, depth + 1));
                if (node.right) node._children.push(prepareNode(node.right, depth + 1));
            } else if (node.node_type === 'UnaryOpNode') {
                if (node.operand) node._children.push(prepareNode(node.operand, depth + 1));
            }
            return node;
        }

        const tree = prepareNode(JSON.parse(JSON.stringify(root)));

        // Position nodes by calculating subtree leaf widths
        let currentX = 50;
        const nodeWidth = 90;
        const levelHeight = 85;

        function assignPositions(node) {
            if (node._children.length === 0) {
                node._x = currentX;
                currentX += nodeWidth;
            } else {
                node._children.forEach(child => assignPositions(child));
                const firstChild = node._children[0];
                const lastChild = node._children[node._children.length - 1];
                node._x = (firstChild._x + lastChild._x) / 2;
            }
            node._y = 40 + (node._depth * levelHeight);
        }

        assignPositions(tree);

        const svgWidth = Math.max(currentX + 60, 600);
        const maxDepth = getMaxDepth(tree);
        const svgHeight = Math.max(120 + (maxDepth * levelHeight), 380);

        // Generate lines and SVG nodes
        let linesHtml = '';
        let nodesHtml = '';

        function renderSvgElements(node) {
            node._children.forEach(child => {
                linesHtml += `<line class="ast-link-line" x1="${node._x}" y1="${node._y}" x2="${child._x}" y2="${child._y}" />`;
                renderSvgElements(child);
            });

            // Node visual representation
            const isOp = node.node_type === 'BinaryOpNode' || node.node_type === 'UnaryOpNode';
            let label = '';
            let subLabel = '';

            if (isOp) {
                label = node.operator_name || node.operator;
                subLabel = `op: '${node.operator}'`;
            } else if (node.node_type === 'NumberNode') {
                label = String(node.value);
                subLabel = 'number';
            } else if (node.node_type === 'BooleanNode') {
                label = node.value ? 'true' : 'false';
                subLabel = 'boolean';
            } else if (node.node_type === 'IdentifierNode') {
                label = node.name;
                subLabel = node.inferred_type ? `id: ${node.inferred_type}` : 'id';
            }

            const circleFill = isOp ? '#312E81' : '#1E293B';
            const strokeColor = isOp ? '#818CF8' : '#38BDF8';

            nodesHtml += `
                <g class="ast-node-group" transform="translate(${node._x}, ${node._y})">
                    <rect x="-38" y="-22" width="76" height="44" rx="8" 
                          fill="${circleFill}" stroke="${strokeColor}" stroke-width="2" class="ast-node-circle" />
                    <text y="-3" class="ast-node-label">${escapeHtml(label)}</text>
                    <text y="12" class="ast-node-sub">${escapeHtml(subLabel)}</text>
                </g>
            `;
        }

        renderSvgElements(tree);

        return `
            <svg class="ast-svg-canvas" width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}" xmlns="http://www.w3.org/2000/svg">
                <g>${linesHtml}</g>
                <g>${nodesHtml}</g>
            </svg>
        `;
    }

    function getMaxDepth(node) {
        if (!node._children || node._children.length === 0) return node._depth;
        return Math.max(...node._children.map(c => getMaxDepth(c)));
    }

    // Toggle AST Views
    btnViewSvg.addEventListener('click', () => {
        btnViewSvg.classList.add('active');
        btnViewText.classList.remove('active');
        astSvgContainer.style.display = 'flex';
        astTextContainer.style.display = 'none';
    });

    btnViewText.addEventListener('click', () => {
        btnViewText.classList.add('active');
        btnViewSvg.classList.remove('active');
        astSvgContainer.style.display = 'none';
        astTextContainer.style.display = 'block';
    });

    // Grammar & Grouping Explanation
    function renderGrammarDerivation(res) {
        if (!res.success || !res.ast) {
            grammarDerivationBox.innerHTML = '<p class="text-muted">Parser did not produce a complete derivation tree due to syntax errors.</p>';
            return;
        }

        let explanation = '<ul style="padding-left: 1.25rem; display: flex; flex-direction: column; gap: 0.45rem;">';
        explanation += `<li><strong>Root Expression:</strong> Evaluated into an AST rooted at <code>${escapeHtml(res.ast.operator_name || res.ast.node_type)}</code>.</li>`;
        
        if (res.expression.includes('||')) {
            explanation += `<li><strong>Logical OR (<code>||</code>):</strong> Lowest operator precedence (Level 5); splits independent clauses into conjunctions.</li>`;
        }
        if (res.expression.includes('&&')) {
            explanation += `<li><strong>Logical AND (<code>&&</code>):</strong> Higher precedence (Level 4) than <code>||</code>; evaluated before OR operators.</li>`;
        }
        if (res.expression.includes('>') || res.expression.includes('<') || res.expression.includes('==') || res.expression.includes('!=')) {
            explanation += `<li><strong>Relational & Equality Comparisons:</strong> Evaluated at Level 3 precedence, producing intermediate Boolean values.</li>`;
        }
        if (res.expression.includes('!')) {
            explanation += `<li><strong>Unary NOT (<code>!</code>):</strong> High right-associative precedence (Level 2); binds directly to its operand.</li>`;
        }
        if (res.expression.includes('(')) {
            explanation += `<li><strong>Parenthesized Expressions:</strong> Explicit grouping forces overridden evaluation priority (Level 1).</li>`;
        }
        explanation += '</ul>';

        grammarDerivationBox.innerHTML = explanation;
    }

    // Semantics Tab
    function renderSemantics(res) {
        const usedVars = res.used_variables || {};
        const varKeys = Object.keys(usedVars);

        if (varKeys.length === 0) {
            usedVariablesTableBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No variable identifiers referenced in expression.</td></tr>';
            return;
        }

        let html = '';
        varKeys.forEach(k => {
            const info = usedVars[k];
            const isDeclared = info.status === 'declared';
            const statusBadge = isDeclared 
                ? '<span class="badge phase-badge badge-success">DECLARED</span>' 
                : '<span class="badge phase-badge badge-failed">UNDECLARED</span>';
            const valStr = info.value !== null && info.value !== undefined ? String(info.value) : '<span class="text-muted">None</span>';

            html += `
                <tr>
                    <td><strong style="color: #38BDF8; font-family: var(--font-mono);">${escapeHtml(info.name)}</strong></td>
                    <td>${statusBadge}</td>
                    <td><span class="badge badge-accent">${escapeHtml(info.declared_type)}</span></td>
                    <td style="font-family: var(--font-mono);">${valStr}</td>
                </tr>
            `;
        });
        usedVariablesTableBody.innerHTML = html;
    }

    // Errors Tab
    function renderErrors(errors, warnings) {
        if ((!errors || errors.length === 0) && (!warnings || warnings.length === 0)) {
            errorsContainer.innerHTML = '<div class="empty-state">✓ No errors or warnings detected. Clean compilation!</div>';
            return;
        }

        let html = '';

        if (errors && errors.length > 0) {
            errors.forEach(err => {
                html += `
                    <div class="error-alert-card">
                        <div class="error-alert-header">
                            <span class="error-badge-category">${escapeHtml(err.category || 'Compiler')} Error</span>
                            <span class="error-loc">Line ${err.line}, Column ${err.column}</span>
                        </div>
                        <div class="error-message">${escapeHtml(err.message)}</div>
                        ${err.suggestion ? `<div class="error-suggestion-box">💡 <strong>Suggested Fix:</strong> ${escapeHtml(err.suggestion)}</div>` : ''}
                    </div>
                `;
            });
        }

        if (warnings && warnings.length > 0) {
            warnings.forEach(w => {
                html += `
                    <div class="error-alert-card" style="border-left-color: var(--color-warning); background: rgba(245, 158, 11, 0.08); border-color: rgba(245, 158, 11, 0.3);">
                        <div class="error-alert-header">
                            <span class="error-badge-category" style="background: rgba(245, 158, 11, 0.2); color: #FBBF24;">Warning</span>
                            <span class="error-loc">Line ${w.line}, Column ${w.column}</span>
                        </div>
                        <div class="error-message" style="color: #FDE68A;">${escapeHtml(w.message)}</div>
                    </div>
                `;
            });
        }

        errorsContainer.innerHTML = html;
    }

    // ==========================================
    // 8. Clipboard Copy Functions
    // ==========================================
    btnCopyTokens.addEventListener('click', () => {
        if (!lastCompilationResult || !lastCompilationResult.tokens) {
            showToast('No tokens to copy', 'error');
            return;
        }
        navigator.clipboard.writeText(JSON.stringify(lastCompilationResult.tokens, null, 2))
            .then(() => showToast('Tokens JSON copied to clipboard!', 'success'))
            .catch(() => showToast('Failed to copy to clipboard', 'error'));
    });

    btnCopyAst.addEventListener('click', () => {
        if (!lastCompilationResult || !lastCompilationResult.ast) {
            showToast('No AST to copy', 'error');
            return;
        }
        navigator.clipboard.writeText(JSON.stringify(lastCompilationResult.ast, null, 2))
            .then(() => showToast('AST JSON copied to clipboard!', 'success'))
            .catch(() => showToast('Failed to copy to clipboard', 'error'));
    });

    // ==========================================
    // 9. Modal / Guide
    // ==========================================
    btnHelp.addEventListener('click', () => {
        modalHelp.classList.add('open');
    });

    btnCloseHelp.addEventListener('click', () => {
        modalHelp.classList.remove('open');
    });

    modalHelp.addEventListener('click', (e) => {
        if (e.target === modalHelp) {
            modalHelp.classList.remove('open');
        }
    });

    // ==========================================
    // 10. Utility Helpers
    // ==========================================
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span>${type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ')}</span>
            <span>${escapeHtml(message)}</span>
        `;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // Run initial startup tasks
    initSymbolTable();
    updateLineNumbers();
    checkBackendHealth();
    // Auto-compile initial expression
    runCompilation();
});

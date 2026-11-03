import javax.swing.BorderFactory;
import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTextField;
import javax.swing.ListSelectionModel;
import javax.swing.SwingUtilities;
import javax.swing.border.EmptyBorder;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.List;

/**
 * A single-file, dependency-free Swing password manager demo.
 *
 * <p>This application intentionally stores entries only in memory. It is a UI
 * demonstration, not secure password storage: closing the window loses data.</p>
 */
public class xp extends JFrame {
    private static final Color NAVY = new Color(31, 49, 74);
    private static final Color ACCENT = new Color(35, 126, 180);
    private static final Color PALE_BLUE = new Color(238, 247, 252);
    private static final String CHARACTERS =
            "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%^&*";

    private final List<Entry> entries = new ArrayList<Entry>();
    private final DefaultListModel<Entry> listModel = new DefaultListModel<Entry>();
    private final JList<Entry> entryList = new JList<Entry>(listModel);
    private final JTextField searchField = new JTextField();
    private final JTextField titleField = new JTextField();
    private final JTextField usernameField = new JTextField();
    private final JTextField urlField = new JTextField();
    private final JComboBox<String> categoryBox =
            new JComboBox<String>(new String[]{"Website", "Email", "Work", "Finance", "Other"});
    private final JPasswordField passwordField = new JPasswordField();
    private final JCheckBox showPassword = new JCheckBox("Show password");
    private final JLabel modeLabel = new JLabel("New entry");
    private final JLabel countLabel = new JLabel("0 entries");
    private final SecureRandom random = new SecureRandom();
    private boolean editing;
    private Entry selectedEntry;

    public xp() {
        super("VaultLite — Password Manager Demo");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setMinimumSize(new Dimension(920, 590));
        setSize(1060, 670);
        setLocationByPlatform(true);
        buildUi();
        refreshList();
        clearForm();
    }

    private void buildUi() {
        JPanel root = new JPanel(new BorderLayout(0, 0));
        root.setBackground(Color.WHITE);
        setContentPane(root);

        JPanel header = new JPanel(new BorderLayout());
        header.setBackground(NAVY);
        header.setBorder(new EmptyBorder(18, 24, 16, 24));
        JLabel brand = new JLabel("VaultLite");
        brand.setForeground(Color.WHITE);
        brand.setFont(new Font("SansSerif", Font.BOLD, 25));
        JLabel subtitle = new JLabel("Password manager demo  •  memory-only storage");
        subtitle.setForeground(new Color(205, 220, 234));
        subtitle.setFont(new Font("SansSerif", Font.PLAIN, 13));
        JPanel heading = new JPanel(new GridLayout(2, 1));
        heading.setOpaque(false);
        heading.add(brand);
        heading.add(subtitle);
        header.add(heading, BorderLayout.WEST);
        JLabel warning = new JLabel("DEMO — NOT SECURE STORAGE");
        warning.setForeground(new Color(255, 214, 122));
        warning.setFont(new Font("SansSerif", Font.BOLD, 12));
        header.add(warning, BorderLayout.EAST);
        root.add(header, BorderLayout.NORTH);

        JPanel sidebar = new JPanel(new BorderLayout(0, 12));
        sidebar.setBackground(new Color(248, 250, 252));
        sidebar.setBorder(new EmptyBorder(18, 18, 18, 12));
        JLabel searchLabel = new JLabel("YOUR ENTRIES");
        searchLabel.setForeground(new Color(86, 103, 121));
        searchLabel.setFont(new Font("SansSerif", Font.BOLD, 11));
        sidebar.add(searchLabel, BorderLayout.NORTH);
        JPanel searchPanel = new JPanel(new BorderLayout(7, 0));
        searchPanel.setOpaque(false);
        searchField.putClientProperty("JTextField.placeholderText", "Search entries...");
        searchPanel.add(searchField, BorderLayout.CENTER);
        JButton clearSearch = new JButton("×");
        clearSearch.setToolTipText("Clear search");
        clearSearch.addActionListener(e -> searchField.setText(""));
        searchPanel.add(clearSearch, BorderLayout.EAST);
        JPanel listWrap = new JPanel(new BorderLayout(0, 8));
        listWrap.setOpaque(false);
        listWrap.add(searchPanel, BorderLayout.NORTH);
        entryList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        entryList.setFixedCellHeight(54);
        entryList.setBorder(BorderFactory.createEmptyBorder(3, 3, 3, 3));
        entryList.addListSelectionListener(e -> {
            if (!e.getValueIsAdjusting()) loadSelectedEntry();
        });
        listWrap.add(new JScrollPane(entryList), BorderLayout.CENTER);
        sidebar.add(listWrap, BorderLayout.CENTER);
        JPanel sideBottom = new JPanel(new BorderLayout());
        sideBottom.setOpaque(false);
        countLabel.setForeground(new Color(100, 115, 130));
        sideBottom.add(countLabel, BorderLayout.WEST);
        JButton newButton = button("+  New entry", ACCENT, Color.WHITE);
        newButton.addActionListener(e -> clearForm());
        sideBottom.add(newButton, BorderLayout.EAST);
        sidebar.add(sideBottom, BorderLayout.SOUTH);

        JPanel form = new JPanel(new BorderLayout(0, 16));
        form.setBackground(Color.WHITE);
        form.setBorder(new EmptyBorder(22, 24, 22, 25));
        JPanel formTitle = new JPanel(new BorderLayout());
        formTitle.setOpaque(false);
        JLabel title = new JLabel("Entry details");
        title.setFont(new Font("SansSerif", Font.BOLD, 22));
        title.setForeground(NAVY);
        formTitle.add(title, BorderLayout.WEST);
        modeLabel.setForeground(ACCENT);
        modeLabel.setFont(new Font("SansSerif", Font.BOLD, 13));
        formTitle.add(modeLabel, BorderLayout.EAST);
        form.add(formTitle, BorderLayout.NORTH);

        JPanel fields = new JPanel(new GridBagLayout());
        fields.setOpaque(false);
        addField(fields, "Title *", titleField, 0);
        addField(fields, "Username / email", usernameField, 1);
        addField(fields, "Website / URL", urlField, 2);
        addField(fields, "Category", categoryBox, 3);
        addField(fields, "Password *", passwordField, 4);
        JPanel passwordTools = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 0));
        passwordTools.setOpaque(false);
        passwordTools.add(showPassword);
        JButton generate = new JButton("Generate password");
        generate.addActionListener(this::generatePassword);
        passwordTools.add(generate);
        GridBagConstraints toolConstraints = constraints(5);
        toolConstraints.gridx = 1;
        fields.add(passwordTools, toolConstraints);
        form.add(fields, BorderLayout.CENTER);

        JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 9, 0));
        actions.setOpaque(false);
        JButton delete = button("Delete", new Color(190, 65, 65), Color.WHITE);
        delete.addActionListener(e -> deleteSelected());
        JButton cancel = new JButton("Clear");
        cancel.addActionListener(e -> clearForm());
        JButton save = button("Save entry", ACCENT, Color.WHITE);
        save.addActionListener(e -> saveEntry());
        actions.add(delete);
        actions.add(cancel);
        actions.add(save);
        form.add(actions, BorderLayout.SOUTH);

        searchField.getDocument().addDocumentListener(new SimpleDocumentListener() {
            public void update() { refreshList(); }
        });
        showPassword.addActionListener(e ->
                passwordField.setEchoChar(showPassword.isSelected() ? (char) 0 : '*'));
        JSplitPane split = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, sidebar, form);
        split.setDividerLocation(315);
        split.setDividerSize(5);
        split.setBorder(null);
        root.add(split, BorderLayout.CENTER);
    }

    private void addField(JPanel panel, String label, java.awt.Component field, int row) {
        GridBagConstraints labelConstraints = constraints(row);
        labelConstraints.gridx = 0;
        labelConstraints.weightx = 0;
        labelConstraints.fill = GridBagConstraints.NONE;
        labelConstraints.anchor = GridBagConstraints.WEST;
        panel.add(new JLabel(label), labelConstraints);
        GridBagConstraints fieldConstraints = constraints(row);
        fieldConstraints.gridx = 1;
        fieldConstraints.weightx = 1;
        fieldConstraints.fill = GridBagConstraints.HORIZONTAL;
        panel.add(field, fieldConstraints);
    }

    private GridBagConstraints constraints(int row) {
        GridBagConstraints c = new GridBagConstraints();
        c.gridy = row;
        c.insets = new Insets(7, 0, 7, 12);
        return c;
    }

    private JButton button(String text, Color background, Color foreground) {
        JButton button = new JButton(text);
        button.setBackground(background);
        button.setForeground(foreground);
        button.setFocusPainted(false);
        return button;
    }

    private void generatePassword(ActionEvent event) {
        int length = 18;
        char[] generated = new char[length];
        for (int i = 0; i < generated.length; i++) {
            generated[i] = CHARACTERS.charAt(random.nextInt(CHARACTERS.length()));
        }
        passwordField.setText(new String(generated));
        showPassword.setSelected(true);
        passwordField.setEchoChar((char) 0);
    }

    private void saveEntry() {
        String title = titleField.getText().trim();
        String password = new String(passwordField.getPassword());
        if (title.isEmpty() || password.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Title and password are required.",
                    "Missing information", JOptionPane.WARNING_MESSAGE);
            return;
        }
        Entry entry = editing ? selectedEntry : new Entry();
        entry.title = title;
        entry.username = usernameField.getText().trim();
        entry.url = urlField.getText().trim();
        entry.category = (String) categoryBox.getSelectedItem();
        entry.password = password;
        if (!editing) entries.add(entry);
        refreshList();
        entryList.setSelectedValue(entry, true);
        selectedEntry = entry;
        editing = true;
        modeLabel.setText("Editing entry");
    }

    private void deleteSelected() {
        if (selectedEntry == null) return;
        int choice = JOptionPane.showConfirmDialog(this,
                "Delete \"" + selectedEntry.title + "\" from this demo vault?",
                "Confirm deletion", JOptionPane.YES_NO_OPTION);
        if (choice == JOptionPane.YES_OPTION) {
            entries.remove(selectedEntry);
            clearForm();
            refreshList();
        }
    }

    private void loadSelectedEntry() {
        Entry entry = entryList.getSelectedValue();
        if (entry == null) return;
        selectedEntry = entry;
        editing = true;
        titleField.setText(entry.title);
        usernameField.setText(entry.username);
        urlField.setText(entry.url);
        categoryBox.setSelectedItem(entry.category);
        passwordField.setText(entry.password);
        modeLabel.setText("Editing entry");
    }

    private void clearForm() {
        selectedEntry = null;
        editing = false;
        entryList.clearSelection();
        titleField.setText("");
        usernameField.setText("");
        urlField.setText("");
        categoryBox.setSelectedIndex(0);
        passwordField.setText("");
        modeLabel.setText("New entry");
    }

    private void refreshList() {
        String query = searchField.getText().trim().toLowerCase();
        listModel.clear();
        for (Entry entry : entries) {
            if (query.isEmpty() || entry.matches(query)) listModel.addElement(entry);
        }
        int visible = listModel.size();
        countLabel.setText(visible + (visible == 1 ? " entry" : " entries"));
    }

    private static class Entry {
        String title = "";
        String username = "";
        String url = "";
        String category = "Website";
        String password = "";

        boolean matches(String query) {
            return title.toLowerCase().contains(query)
                    || username.toLowerCase().contains(query)
                    || url.toLowerCase().contains(query)
                    || category.toLowerCase().contains(query);
        }

        public String toString() {
            return title + (username.isEmpty() ? "" : "\n" + username);
        }
    }

    private abstract static class SimpleDocumentListener
            implements javax.swing.event.DocumentListener {
        public void insertUpdate(javax.swing.event.DocumentEvent e) { update(); }
        public void removeUpdate(javax.swing.event.DocumentEvent e) { update(); }
        public void changedUpdate(javax.swing.event.DocumentEvent e) { update(); }
        public abstract void update();
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new xp().setVisible(true));
    }
}

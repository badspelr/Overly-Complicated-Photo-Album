document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-category-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const categoryName = this.dataset.categoryName;
            if (!confirm(`Are you sure you want to delete the category "${categoryName}"?`)) {
                event.preventDefault();
            }
        });
    });
});

#!/usr/bin/env python3
"""
Test Folders Cleanup Script
Deletes all JSON and PNG files from section_*_*_test folders to clean up after processing.
"""

import os
import shutil
from pathlib import Path

class TestFoldersCleanup:
    def __init__(self):
        """Initialize the cleanup script with all section test folder paths"""
        # Make base directory relative to the project root
        # Get project root (two levels up from src/utils/)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.base_dir = project_root
        self.test_folders = [
            "data/test_sections/section_1_1_test",
            "data/test_sections/section_1_2_test", 
            "data/test_sections/section_1_3_test",
            "data/test_sections/section_1_4_test",
            "data/test_sections/section_2_1_test",
            "data/test_sections/section_2_2_test",
            "data/test_sections/section_2_2_part1_test",  # NEW: Two-part section 2_2
            "data/test_sections/section_2_2_part2_test",  # NEW: Two-part section 2_2
            "data/test_sections/section_2_3_test",
            "data/test_sections/section_2_4_test", 
            "data/test_sections/section_2_5_test",
            "data/test_sections/section_3_2_test",
            "data/test_sections/section_3_3_test",
            "data/test_sections/section_3_4_test",
            "data/test_sections/section_4_1_test",
            "data/test_sections/section_4_1_part1_test",  # NEW: Two-part section 4_1
            "data/test_sections/section_4_1_part2_test",  # NEW: Two-part section 4_1
            "data/test_sections/section_4_2_test",
            "data/test_sections/section_4_3_test",
            "data/test_sections/section_4_4_test",
            "data/test_sections/section_4_5_test",
            "data/test_sections/section_4_6_test"  # NEW: Section 4_6 was missing
        ]
    
    def cleanup_all_folders(self, verbose=True) -> dict:
        """
        Clean up all test folders by removing JSON and PNG files
        
        Returns:
            dict: Results of cleanup operation with statistics
        """
        results = {
            "folders_processed": 0,
            "files_deleted": 0,
            "folders_not_found": 0,
            "errors": []
        }
        
        if verbose:
            print("🧹 Starting Test Folders Cleanup...")
            print("=" * 50)
        
        for folder_name in self.test_folders:
            folder_path = os.path.join(self.base_dir, folder_name)
            
            if not os.path.exists(folder_path):
                results["folders_not_found"] += 1
                if verbose:
                    print(f"⚠️  Folder not found: {folder_name}")
                continue
            
            try:
                files_in_folder = 0
                
                # Find all JSON and PNG files in the folder
                for file_path in Path(folder_path).glob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in ['.json', '.png']:
                        try:
                            os.remove(file_path)
                            files_in_folder += 1
                            if verbose:
                                print(f"   🗑️  Deleted: {file_path.name}")
                        except Exception as e:
                            results["errors"].append(f"Error deleting {file_path}: {e}")
                            if verbose:
                                print(f"   ❌ Error deleting {file_path.name}: {e}")
                
                results["folders_processed"] += 1
                results["files_deleted"] += files_in_folder
                
                if verbose:
                    if files_in_folder > 0:
                        print(f"✅ Cleaned {folder_name}: {files_in_folder} files deleted")
                    else:
                        print(f"📂 {folder_name}: Already clean (no files to delete)")
                        
            except Exception as e:
                results["errors"].append(f"Error processing {folder_name}: {e}")
                if verbose:
                    print(f"❌ Error processing {folder_name}: {e}")
        
        if verbose:
            print("=" * 50)
            print(f"🎯 Cleanup Complete!")
            print(f"   📊 Folders processed: {results['folders_processed']}")
            print(f"   🗑️  Total files deleted: {results['files_deleted']}")
            if results['folders_not_found'] > 0:
                print(f"   ⚠️  Folders not found: {results['folders_not_found']}")
            if results['errors']:
                print(f"   ❌ Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"      • {error}")
        
        return results
    
    def cleanup_specific_folder(self, folder_name: str, verbose=True) -> dict:
        """
        Clean up a specific test folder
        
        Args:
            folder_name (str): Name of the folder to clean (e.g. 'section_1_1_test')
            verbose (bool): Whether to print progress messages
            
        Returns:
            dict: Results of cleanup operation
        """
        results = {
            "folder": folder_name,
            "files_deleted": 0,
            "folder_found": False,
            "errors": []
        }
        
        folder_path = os.path.join(self.base_dir, folder_name)
        
        if not os.path.exists(folder_path):
            if verbose:
                print(f"⚠️  Folder not found: {folder_name}")
            return results
        
        results["folder_found"] = True
        
        try:
            # Find all JSON and PNG files in the folder
            for file_path in Path(folder_path).glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.json', '.png']:
                    try:
                        os.remove(file_path)
                        results["files_deleted"] += 1
                        if verbose:
                            print(f"   🗑️  Deleted: {file_path.name}")
                    except Exception as e:
                        results["errors"].append(f"Error deleting {file_path}: {e}")
                        if verbose:
                            print(f"   ❌ Error deleting {file_path.name}: {e}")
            
            if verbose:
                if results["files_deleted"] > 0:
                    print(f"✅ Cleaned {folder_name}: {results['files_deleted']} files deleted")
                else:
                    print(f"📂 {folder_name}: Already clean (no files to delete)")
                    
        except Exception as e:
            results["errors"].append(f"Error processing {folder_name}: {e}")
            if verbose:
                print(f"❌ Error processing {folder_name}: {e}")
        
        return results


def main():
    """Command line interface for the cleanup script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up test folders after post-review processing")
    parser.add_argument("--folder", help="Specific folder to clean (e.g. section_1_1_test)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Run quietly without progress messages")
    
    args = parser.parse_args()
    
    cleanup = TestFoldersCleanup()
    
    if args.folder:
        # Clean specific folder
        results = cleanup.cleanup_specific_folder(args.folder, verbose=not args.quiet)
        if results["errors"]:
            exit(1)
    else:
        # Clean all folders
        results = cleanup.cleanup_all_folders(verbose=not args.quiet)
        if results["errors"]:
            exit(1)
    
    exit(0)


if __name__ == "__main__":
    main()
